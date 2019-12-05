from py2neo import *
from KgExceptions import *
import uuid
import yaml
import logging
import requests

kgexceptions = KgExceptions()

class KgService(object):
    # initialize the graph

    def __init__(self, url, user, pwd, path=''):
        """
        This function initializes the KgService.

        Parameters
        ----------
        url : string
            enter here the IP adress of the host running neo4j
        user : string
            enter here the username to login to neo4j
        pwd : string
            enter here the password to login to neo4j
        path : string
            set the directory path to your config.yaml
            e.g.: "", if config in root directory of where KgService is called
            e.g.: "conf/", if config one level below root directory
            e.g.: "../conf/", if config one level above root directoy
        Returns
        -------
        nothing

        """
        self.initialize_logger()
        # NOTE: Many attributes are set inside config parser
        self._config_parser(path)
        self.graph = Graph(url, auth=(user, pwd))
        self.verify_and_set_tags(self.model, self.meta)
        self._initialize_db_constraints()

    # _config_parser: json parser for config file
    # NOTE: Many attributes are set here
    def _config_parser(self, path=''):
        filename = 'config.yaml'
        filename = path + filename
        with open(filename, 'r') as f:
            self.config = yaml.safe_load(f)
        self.blacklist = self.config['BLACKLIST']
        terms = self.config['TERMS']
        for term in terms:
            prop = term.keys()[0]
            val = term.values()[0]
            if prop == 'subclass_of':
                self.subclass_of = val
            elif prop == 'instance_of':
                self.instance_of = val
            elif prop == 'identifier':
                self.identifier = val
            elif prop == 'model':
                self.model = val
            elif prop == 'meta':
                self.meta = val

    def verify_and_set_tags(self, model, meta):
        if model:
            self.model = model
            self.verify_inputs(self.model)
        if meta:
            self.meta = meta
            self.verify_inputs(self.meta)

    def initialize_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s' +
                            ' %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename='logfile.log')

    def verify_inputs(self, input):
        if self.invalid_label(input):
            raise ValueError('Illegal label name "%s".' +
                             'Only Alpha-numeric and "_" allowed.' +
                             'This label will not be assigned.' % input)

    def _initialize_db_constraints(self):
        # q='CREATE CONSTRAINT ON (a) ASSERT a.%s IS UNIQUE;' (self.identifier)
        # q2= create index on self.identifier
        # run query
        pass

    def invalid_label(self, l):
        return l and not l.replace('_', '').isalnum()

    # @abstractmethod
    # def get_model_label(self):
    #     return model

# ----- TBox Functions:
    def get_subtypes(self, class_identifier, direct_children, include_self):
    	"""
		Given a class identifier returns all the decendants of the Node.

        Parameters
        ----------
        class_identifier : identifier
        direct_children : Bool
            defaults to False if not specified. If set to true only returns
            the direct children of class_identifier, otherwise all the
            decendants.
        include_self : Bool
            defaults to True if not specified. If True it includes the
            node class_identifier in the returned data, otherwise
            class_identifier node is omited.

        Returns
        -------
        payload : pl
            returns all subtypes within payload
    	"""
        deg = 1 if direct_children else -1
        results = self._get_path(class_identifier, rel="subclass_of", inv=True, degree=deg, inc_self=include_self)
        temp_lis=[]
        for res in results:
            temp_lis.append({self.identifier:res})
        pld=self.get({'payload':temp_lis})
    	return pld

    def get_attributes(self, identifier):
    	"""
    	Takes a class uri a retuns a list of the names of all the properties
        and relations of that class.

        Parameters
        ----------
        identifier : identifier
            identifier of a class

        Returns
        -------
        result : list
            a list of names of all properties and relations
    	"""
        result = []
        obj_props = []
        tmp_list = []
        antecedents = self._get_path(identifier, rel="subclass_of", inv=False, degree=-1, inc_self=True)
        req_props = self._get_path(antecedents, rel="required_property", inv=False, degree=-1, out='title', inc_self=False)
        result.extend(req_props)
        opt_props = self._get_path(antecedents, rel="optional_property", inv=False, degree=-1, out='title', inc_self=False)
        result.extend(opt_props)
        query = 'MATCH (n{identifier: {identifier}})-[r:object_property]->(i) RETURN r.title'
        for antecedent in antecedents:
            rel_title = self.graph.run(query, parameters={"identifier": antecedent})
            tmp_list.extend(rel_title.data())
        for d in tmp_list:
            for value in d.values():
                obj_props.append(value)
        result.extend(obj_props)
        return result

    def get_att_type(self, att_title):
        """
        A function that takes a string name of a property or
        relationship and returns its type.

        Parameters
        ----------
        att_title : string
            title of attribute

        Returns
        -------
        att_type : string
            type of attribute
        """
        att_type = ""
        if att_title == self.identifier:
            att_type = 'identifier'
        elif att_title == self.instance_of:
            att_type = 'type'
        else:
            try:
                matcher = NodeMatcher(self.graph)
                node = matcher.match(title=att_title)
                node = node.first()
                if node:
                    att_type = node['xsd_type']
            except Exception as e:
                self.logger.info(str(e))
            try:
                matcher = RelationshipMatcher(self.graph)
                rel = matcher.match(title=att_title)
                rel = rel.first()
                if rel:
                    end_node = rel.end_node
                    att_type = 'ref ' + str(end_node['title'])
            except Exception as e:
                self.logger.info(str(e))
        return att_type

    # returns node by given title
    def _internal_get_node_by_title(self, title):
        query = "MATCH (n) WHERE toLower(n.title)=toLower({title}) RETURN n"
        node = self.graph.run(query, parameters={"title":title})
        node = node.data()[0]['n']
        node_id = node['identifier']
        payload = {self.identifier: node_id}
        node = self._get_helper(payload)
        return node

    # return tbox node by given title
    def _get_tbox_node_by_title(self, class_title, prop_name=None):
        try:
            node = self._internal_get_node_by_title(class_title)
        except Exception as e:
            self.logger.info(str(e))
            if prop_name:
                return None
            else:
                return self._format_output([])
        if prop_name:
            if prop_name in node.keys():
                return node[prop_name]
            else:
                return None
        return self._format_output(node)


# ----- CRUD functions:

#CREATE
# the create function and its corresponding helper functions (listed below)
# allow to add new instances to the graph
    def create(self, payload, user=None):
        """
        This function creates instances and also allows to
        directly create relations and properties.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'payload': [{'att1': val1, ...}, {'att1': val1, ...}]}
            att[i] : relation or property
        user : identifier
            Optional parameter. If available, given user will receive
            email notifications.

        Example input
        -------------
        {'payload': [{
            "title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": "http://example.org/user",
            "description": "Employee"
        }]}

        Returns
        -------
        payload : pl (see format above)
            Returns the newly created instance and its relations and
            properties.

        Example output
        --------------
        {'payload': [{
            "title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": "http://example.org/user",
            "description": "Employee",
            "identifier": "http://example.org/xyz123"
        }]}
        """
        instance_of = self.instance_of
        nodes = []
        try:
            payload = self._validate_and_extract_input(payload)
        except Exception as e:
            self.logger.warning(str(e))
            return self._format_output([])
        for instance in payload:
            try:
                node = self._create(instance)
                if node:
                    nodes.append(node)
            except Exception as e:
                self.logger.warning(str(e))
                # return self._format_output([])
        return self._format_output(nodes)

    def _create(self, instance):
        """
        This function takes a dict of attributes and creates a node out of it.

        Parameters
        ----------
        instance : dict of attributes
            attributes may be either properties or relations

        Returns
        -------
        node : dict

        Example output
        --------------
        {'identifier': 'http://e.org/80e5',
        'type': ['http://example.org/project'], 'description': 'Project',
        'title': 'Future IOT'}
        """
        instance_of = self.instance_of
        identifier = self.identifier
        if self._check_valid_input_create(instance) is not True:
            return None
        class_id = instance[instance_of]
        # create new node
        node_id = self._create_node(class_id)
        del instance[instance_of]
        if identifier in instance.keys():
            return None
        self._set_attributes(node_id, instance, class_id)
        payload = {identifier: node_id}
        node = self._get_helper(payload)
        return node

    def _create_node(self, class_id):
        """
        This function takes a class id and creates a node of type class id.

        Parameters
        ----------
        class_id : identifier

        Returns
        -------
        identifier : identifier
        """
        properties = {}
        identifier = self._identifier_generator()
        properties[self.identifier] = identifier
        # create node
        query = "MERGE (s:%s {identifier:{class_id}}) CREATE (i:%s {properties})-[:%s]->(s) RETURN i" % (self.meta, self.model, self.instance_of)
        self.graph.run(query, parameters={"properties": properties,
                                          "class_id": class_id})
        return identifier

    def _check_valid_input_create(self, instance):
        """
        This function checks if a given dict fulfills the requirements of
        the domain model.

        Parameters
        ----------
        instance : dict

        Returns
        -------
        True : Bool
        False : Bool
        """
        instance_of = self.instance_of
        if instance_of not in instance:
            e = kgexceptions._exception_type_empty(instance)
            self.logger.warning(str(e))
            return False
        class_identifier = instance[instance_of]
        if not self._is_existant(class_identifier):
            e = kgexceptions._exception_non_existant(str(instance))
            self.logger.warning(str(e))
            return False
        req_prop = self._get_req_props(class_identifier)
        if self._validate_req_props_create(req_prop, instance):
            return True

    def _validate_req_props_create(self, req_prop, instance):
        """
        This function checks if a given dict fulfills the required properties,
        defined in the domain model.

        Parameters
        ----------
        req_prop : list of strings
            the list contains the required properties for an instance
            of a certain type.
        instance : dict

        Returns
        -------
        True : Bool
        False : Bool
        """
        for rp in req_prop:
            if rp == self.identifier:
                continue
            if rp not in instance.keys():
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                self.logger.warning(str(e))
                return False
            elif self._is_empty(instance[rp]):
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                self.logger.warning(str(e))
                return False
        return True

#QUERY
# the query function and its corresponding helper functions (listed below)
# allow to directly query the graph via cypher language (excl. blacklist)
    def query(self, query):
        """
        This function allows to perform cypher queries. Modifying operations
        are excluded.

        Parameters
        ----------
        query : cypher query

        Example input
        -------------
        "MATCH (n) WHERE n.name = 'Mr N.K.' RETURN n.mbox"

        Returns
        -------
        payload : pl (see format above)
            Returns the query result

        Example output
        --------------
        {'payload': [{"n.mbox": "n.k@uni-bamberg.de"}]}
        """
        try:
            self._validate_query(query)
            # run query
            result = self.graph.run(query)
            result_data = result.data()
            if not result_data:
                e = kgexceptions._exception_cypher(str(query))
                raise e
        except Exception as e:
            self.logger.warning(str(e))
            return self._format_output([])
        else:
            return self._format_output(result_data)

    def _validate_query(self, query):
        """
        This function checks if a given query is not empty or a modifying
        operation. It raises an exception if the requirements are not
        fulfilled.

        Parameters
        ----------
        query : cypher query
        """
        if self._is_empty(query):
            e = kgexceptions._exception_empty()
            raise e
        if self._injection_check(query):
            e = kgexceptions._exception_blacklisted(query)
            raise e

    def _injection_check(self, query):
        """
        This function checks if a given query is a modifying operation.
        It returns if a modifying opertation is found.

        Parameters
        ----------
        query : cypher query
        """
        query = query.strip()
        return any(word in query.lower() for word in self.blacklist)

#GET
# the get function and its corresponding helper functions (listed below)
# allow to identify an instance of the graph and its attributes and relations
    def get(self, payload):
        """
        This function queries for all attributes (i.e. relations and
        properties) of a given instance and returns them if found.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'payload': [{'identifier': val1}, {'identifier': val2}]}
            identifier[i] : identifier

        Example input
        -------------
        {'payload': [{"identifier": "http://example.org/xyz123"}]}

        Returns
        -------
        payload : pl (see format above)
            Returns the instance and its relations and properties.

        Example output
        --------------
        {'payload': [{
            "title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": "http://example.org/user",
            "description": "Employee",
            "identifier": "http://example.org/xyz123"
        }]}
        """
        nodes = []
        try:
            identifiers = self._validate_and_extract_input(payload)
        except Exception as e:
            self.logger.warning(str(e))
            return self._format_output([])
        for identifier in identifiers:
            try:
                node = self._get_helper(identifier)
                if node:
                    nodes.append(node)
            except Exception as e:
                self.logger.warning(str(e))
                # return self._format_output([])
        return self._format_output(nodes)

    def _get_helper(self, payload):
        """
        This function evaluates properties and relations of a given instance
        and returns them.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'identifier': val1}
            identifier : identifier
        """
        query = 'MATCH (n{identifier: {identifier}})-[r]->(i) RETURN n, TYPE(r), i.identifier'
        relations = {}
        identifier = payload[self.identifier]
        identifier = self._identifier_check(identifier)
        # run query
        path = self.graph.run(query, parameters={"identifier": identifier})
        path = path.data()
        for d in path:
            node = d['n']
            rel_type = d['TYPE(r)']
            identifier = d['i.identifier']
            # handling existant relation keys: append values to list:
            if rel_type in relations.keys():  # case: multiple relation keys
                relations[rel_type].append(identifier)
            else:  # case: relation key only used once
                relations[rel_type] = [identifier]
        result_data = dict(node)
        result_data.update(relations)
        return result_data

#GET instances
# the get instances function allows to identify instances of a given class
    def get_instances(self, identifier):
        """
        This function takes a class identifier and returns all its instances.

        Parameters
        ----------
        identifier : identifier
            the identifier needs to be a class identifier

        Example input
        -------------
        "http://example.org/user"

        Returns
        -------
        payload : pl (see format above)
            Returns a list of dicts. The dicts contain the instances.

        Example output
        --------------
        {'payload': [{
            "title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": "http://example.org/user",
            "description": "Employee",
            "identifier": "http://example.org/xyz123"
        }]}
        """
        # self.logger.debug('Running get_instances for id %s' % (identifier))
        result = self.get_self_descendants(identifier)
        instances = self._get_path(result, rel="type", inv=True, degree=-1)
        # format the output for get to accept it
        res_list=[]
        for id in instances:
            res_list.append({self.identifier:id})
        instances = {'payload': res_list}
        instances = self.get(instances)
        return instances

#UPDATE
# the update function and its corresponding helper functions (listed below)
# allow to modify instances existing on the graph
    def update(self, payload, user=None):
        """
        This function updates one or more instances, i.e. it sets new
        properties and relations.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'payload': [{'att1': val1, 'identifier': id}]}
            att[i] : relation or property
            identifier : identifier

        Example input
        -------------
        {'payload': [{
            "title": "Mr NK new",
            "identifier": "http://example.org/xyz123"
        }]}

        Returns
        -------
        payload : pl (see format above)
            Returns the updated instance(s) and its relations and
            properties.

        Example output
        --------------
        {'payload': [{
            "title": "Mr NK new",
            "mbox": "n.k@uni-bamberg.de",
            "type": "http://example.org/user",
            "description": "Employee",
            "identifier": "http://example.org/xyz123"
        }]}
        """
        nodes = []
        try:
            payload = self._validate_and_extract_input(payload)
        except Exception as e:
            self.logger.warning(str(e))
            return self._format_output([])
        for instance in payload:
            try:
                node = self._update(instance)
                if node:
                    nodes.append(node)
            except Exception as e:
                self.logger.warning(str(e))
                # return self._format_output([])
        return self._format_output(nodes)

    def _update(self, instance):
        """
        This function updates an instance, i.e. it sets new properties
        and relations.

        Parameters
        ----------
        instance : dict
            the dict contains an identifier and the attributes to be
            changed / newly set
        """
        if self._check_valid_input_update(instance) is not True:
            return None
        instance, identifier = self._delete_shared_items(instance)
        class_id = self._get_type(identifier)
        self._set_attributes(identifier, instance, class_id)
        payload = {self.identifier: identifier}
        node = self._get_helper(payload)
        return node

    def _check_valid_input_update(self, instance):
        """
        This function checks if a given dict fulfills the requirements of
        the domain model.

        Parameters
        ----------
        instance : dict

        Returns
        -------
        True : Bool
        False : Bool
        """
        if self.identifier not in instance:
            e = kgexceptions._exception_non_existant(str(instance))
            self.logger.warning(str(e))
            return False
        identifier = instance[self.identifier]
        if not self._is_existant(identifier):
            e = kgexceptions._exception_non_existant(str(instance))
            self.logger.warning(str(e))
            return False
        class_identifier = self._get_type(identifier)
        req_prop = self._get_req_props(class_identifier)
        for rp in req_prop:
            if rp in instance.keys():
              if self._is_empty(instance[rp]):
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                self.logger.warning(str(e))
                return False
        return True

    def _delete_shared_items(self, d):
        """
        This function removes from a given dict the key-value pairs which are
        already assigned to the node. And afterwards returns the updated dict
        and also the instance's identifier.
        """
        identifier = d[self.identifier]
        pl = {self.identifier: identifier}
        node = self._get_helper(pl)
        shared_items = {k: node[k] for k in node if k in d and node[k] == d[k]}
        map(d.pop, shared_items)
        return d, identifier

#DELETE
# the delete function and its corresponding helper functions (listed below)
# allow to delete existing instances from the graph
    def delete(self, payload, user=None):
        """
        This function deletes instances and outputs True if successful.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'payload': [{'identifier1': id1}, {'identifier2': val2}]}
            identifier[i] : identifier

        Example input
        -------------
        {'payload': [{"identifier": "http://example.org/xyz123"}]}

        Returns
        -------
        True : Bool
        False : Bool

        Example output
        --------------
        True
        """
        nodes = []
        instances = []
        try:
            identifiers = self._validate_and_extract_input(payload)
        except Exception as e:
            self.logger.warning(str(e))
            nodes.append(False)
            return nodes
        else:
            for identifier in identifiers:
                try:
                    node = self._delete_helper(identifier)
                    nodes.append(node)
                except Exception as e:
                    self.logger.warning(str(e))
                    nodes.append(False)
                    # return self._format_output([])
        return nodes

    def _delete_helper(self, payload):
        """
        This function deletes an instance and outputs True if successful.

        Parameters
        ----------
        payload : pl (see format below)
        pl : {'payload': [{'identifier1': id}]}
            identifier : identifier
        """
        query = 'MATCH (n) WHERE n.identifier={identifier} DETACH DELETE n'
        tag = ':%s' % self.model
        identifier = payload[self.identifier]
        identifier = self._identifier_check(identifier)
        node = self._node_matcher(identifier).first()
        if tag not in str(node.labels): # check if node is ABox
            e = kgexceptions._exception_delete(str(node))
            raise e
        self.graph.run(query, parameters={"identifier": identifier})
        return True

#Common
# the following functions are used by various functions
    def _set_attributes(self, identifier, instance, class_id):
        """
        This function sets new attributes to an instance, after validation.

        Parameters
        ----------
        identifier : identifier
            the identifier of an instance
        instance : dict
            a dict containing all attributes to be updated / newly set
        class_id : identifier
            the identifier of the corresponding class to the instance
        """
        for attr_name, attr_val in instance.items():
            attr_val = self._listify(attr_val)
            for obj in attr_val:
                if self._valid_relation(identifier, attr_name, obj):
                    self._create_rel(identifier, attr_name, obj)
                elif self._valid_property(attr_name, class_id, ns=False):
                    self._create_prop(identifier, attr_name, obj)
                else:
                    stmt = ("'%s' is not a valid property or relation," +
                            " or it is empty. Hence it will not be created. \n" +
                            "You can safely ignore this, if intended." +
                            " Your input: '%s'") % (attr_name, instance)
                    self.logger.info(stmt)
        return True

    def get_self_descendants(self, identifier):
        """
        see _get_path function
        """
        result = self._get_path(identifier, rel="subclass_of", inv=True, degree=-1, inc_self=True)
        return result

    def _get_path(self, identifiers, rel, inv, degree=-1, out='identifier', inc_self=False):
        """
        This function follows and inherits a path, defined by the parameters
        and returns the visited nodes.

        Parameters
        ----------
        identifiers : list of identifiers
        rel : relation
        inv : inverse, True or False
            inv changes the direction of the arrow (i.e. is identifier start-
            or end-node)
        degree : int
            how deep to iterate, defaults to 1
        out : property
            the value of the specified property will be returned.
            defaults to identifier.
        inc_self : Bool
            if set to True, the given node is included in the result set.
            defaults to False.
        """
        path = []
        if not isinstance(identifiers, list):
            identifiers = [identifiers]
        for identifier in identifiers:
            result = self.__get_path(identifier, rel, inv, degree, out, inc_self)
            path.extend(result)
        return path

    def __get_path(self, identifier, rel, inv, degree=-1, out='identifier', inc_self=False):
        """
        see _get_path function
        """
        result_list = []
        left = ''
        right = '>'
        if inv:
            left = '<'
            right = ''
        card = 0 if inc_self else 1
        query=''
        if degree == 1:
            query = 'MATCH (n{identifier: {identifier}})%s-[r:%s]-%s(i) RETURN i.%s' % (left, rel, right, out)
        else:
            query = 'MATCH (n{identifier: {identifier}})%s-[r:%s*%s..]-%s(i) RETURN i.%s' % (left, rel, card, right, out)
        result = self.graph.run(query, parameters={"identifier": identifier})
        result = result.data()
        for d in result:
            for k, v in d.items():
                result_list.append(v)
        return result_list

    def get_prop_val(self, identifier, prop_name):
        """
        This function evaluates and returnes a property's value by given
        identifier and property name.

        Parameters
        ----------
        identifier : identifiers
        prop_name : property


        Example input
        -------------
        "http://example.org/kbmsthing", "title"

        Returns
        -------
        payload : string

        Example output
        --------------
        "KBMSThing"
        """
        try:
            node = self._node_matcher(identifier)
            node = node.first()
            prop_val = node[prop_name]
        except:
            prop_val = None
        return prop_val

    # return ancestors of given identifier
    def get_self_ancestors(self, identifier):
        ancestor = self._get_path(identifier, rel="type", inv=False,
                                  degree=-1)
        ancestors = self._get_path(ancestor, rel="subclass_of", inv=False,
                                   degree=-1)
        ancestors.extend(ancestor)
        return ancestors


# ----- private functions (only called internally within this class):


    # _is_empty: checks if given payload is empty in our definition
    def _is_empty(self, payload):
        list_empty = ["", " ", False, None, [], {}]
        return payload in list_empty

    # matching node by given identifier
    def _node_matcher(self, identifier):
        matcher = NodeMatcher(self.graph)
        node = matcher.match(identifier=identifier)
        return node

    # is existant: checks given identifier for existing node
    def _is_existant(self, identifier):
        existant = self._node_matcher(identifier)
        return existant

    # checks if given identifier is an instance
    def _is_instance(self, identifier):
        label = ':%s' % self.model
        if self._is_label(identifier, label):
            return True
        else:
            return False

    # checks if given identifier is a class
    def _is_class(self, identifier):
        label = ':%s' % self.meta
        if self._is_label(identifier, label):
            return True
        else:
            return False

    # checks if given instance and label fit together
    def _is_label(self, identifier, label):
        try:
            identifier = self._identifier_check(identifier)
            node = self._node_matcher(identifier).first()
        except Exception as e:
            self.logger.info(str(e))
            return False
        if label not in str(node.labels):
            return False
        return True

    # identifier generator: generates random identifier (= domain name + uuid)
    def _identifier_generator(self):
        domain_name = self.config['DOMAIN_NAME']
        for i in range(10):
            # generating random uuid
            unique_id = uuid.uuid4()
            # forming identifier
            identifier = str(domain_name) + "/" + str(unique_id)
            if not self._is_existant(identifier):
                return identifier
            else:  # This identifier is already in use. Generating a new one.
                i += 1

    # checks if identifier existant
    def _identifier_check(self, identifier):
        identifier = identifier.strip()
        if not self._is_existant(identifier):
            e = kgexceptions._exception_non_existant(str(identifier))
            raise e
        return identifier

    # get class of a given instance
    def _get_type(self, identifier, title=False):
        node = {self.identifier: identifier}
        result = self._get_helper(node)[self.instance_of][0]
        if title:
            node = {self.identifier: result}
            result = self._get_helper(node)['title']
        return result

    # make given elem a list, if is not already
    def _listify(self, elem):
        if not isinstance(elem, list):
            elem = [elem]
        return elem

    # creates properties for given instance
    def _create_prop(self, identifier, attr_name, attr_val):
        attr_name = attr_name.lower()
        # Note: attr_name is set differently because py2neo does not
        #       allow to set labels with parameters
        qa = 'MATCH (n) WHERE n.identifier = {identifier} SET n.%s = {attr_val} RETURN n' % attr_name
        # run query for setting properties
        self.graph.run(qa, parameters={"identifier": identifier,
                                       "attr_val": attr_val})

    # creates relations for given instance
    def _create_rel(self, identifier_start, attr_name, identifier_end):
        attr_name = attr_name.lower()
        # Note: attr_name is set differently because py2neo does not
        #       allow to set labels with parameters
        qr = 'MERGE (s{identifier:{identifier_end}}) MERGE (i{identifier:{identifier_start}}) CREATE (i)-[:%s]->(s) RETURN i' % attr_name
        # run query for setting relations
        self.graph.run(qr, parameters={"identifier_end": identifier_end,
                                       "identifier_start": identifier_start})

    # check if input is empty, return its content
    def _validate_and_extract_input(self, payload):
        if self._is_empty(payload):
            e = kgexceptions._exception_empty()
            raise e
        if 'payload' not in payload:
            e = kgexceptions._exception_empty()
            raise e
        content = payload['payload']
        if self._is_empty(content):
            e = kgexceptions._exception_empty()
            raise e
        return content

    # format the output to json
    def _format_output(self, node_list):
        if not isinstance(node_list, list):
            node_list = [node_list]
        payload = {'payload': node_list}
        return payload

    # checks if given property is a valid property following domain model
    def _valid_property(self, property, class_identifier, ns=False):
        property = property.lower()
        temp_list = [class_identifier]
        anscestors_self = self._get_path(class_identifier, rel="subclass_of",
                                         inv=False, degree=-1)
        temp_list.extend(anscestors_self)
        req_props = self._get_path(temp_list, rel="required_property",
                                   inv=False, degree=-1, out='title')
        opt_props = self._get_path(temp_list, rel="optional_property",
                                   inv=False, degree=-1, out='title')
        return property in req_props or property in opt_props

    # checks if given relation is a valid realtion following domain model
    def _valid_relation(self, sub, rel, obj):
        rel = rel.lower()
        sub_ancestors = self.get_self_ancestors(sub)
        obj_ancestors = self.get_self_ancestors(obj)
        valid_obj = self._get_relation_path(sub_ancestors, rel)
        return any(x in valid_obj for x in obj_ancestors)

    # follow path by given identifier and relation
    def _get_relation_path(self, identifiers, rel):
        temp_list = []
        if not isinstance(identifiers, list):
            identifiers = [identifiers]
        for identifier in identifiers:
            result = self.__get_relation_path(identifier, rel)
            if not any(x in result for x in temp_list):
                temp_list.extend(result)
        return temp_list

    # see _get_relation_path
    def __get_relation_path(self, identifier, rel):
        result_list = []
        query = 'MATCH (n{identifier: {identifier}})-[r:object_property{title: {rel}}]->(i) RETURN i.identifier'
        result = self.graph.run(query, parameters={self.identifier: identifier,
                                                   'rel': rel})
        result = result.data()
        for d in result:
            for k, v in d.items():
                result_list.append(v)
        return result_list

    # get required properties for a given class id, following domain model
    def _get_req_props(self, class_identifier, namespace=False):
        req_props = []
        ancestors = self._get_path(class_identifier, rel="subclass_of",
                                   inv=False, degree=-1)
        ancestors.append(str(class_identifier))
        props = self._get_path(ancestors, rel="required_property",
                               inv=False, degree=-1, out='title')
        if not any(x in props for x in req_props):
            req_props.extend(props)
        return req_props
