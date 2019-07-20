from abc import ABCMeta, abstractmethod
from py2neo import *#Graph, NodeMatcher, RelationshipMatcher
from KgExceptions import *
import uuid
import yaml
import logging
import requests

logger = None
kgexceptions = KgExceptions()

class KgService(object):
    __metaclass__ = ABCMeta
    # initialize the graph
    def __init__(self, url, user, pwd, model, meta, path=''):
        self._config_parser(path)
        self.initialize_logger()
        self.graph = Graph(url, auth=(user, pwd))
        self.verify_and_set_tags(model, meta)
        self._initialize_db_constraints()

    def verify_and_set_tags(self, model, meta):
        if model:
            self.model = model
            self.verify_inputs(self.model)
        if meta:
            self.meta = meta
            self.verify_inputs(self.meta)

    def initialize_logger(self):
        global logger
        base_logger_name = self.parent_logger_name
        logger = logging.getLogger(base_logger_name + '.kgservice')
        logger.setLevel(logging.DEBUG)
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

    @abstractmethod
    def get_model_label(self):
        pass

# ----- CRUD functions:

    # only for testing purposes
    def _clear_all(self):
        self.graph.run('MATCH (n:%s) DETACH DELETE n' % 'ABox')
        # pass

    # create: create node, properties and relations
    # input: {'payload':[{'type': 'ac34rbd', 'title': 'Stephane Bechtel',
    #                    'uploader':'gx84ert'}]}
    # output: {'payload:[{'type': ['ac34rbd'], self.identifier: 'cbd4711',
    #                  'uploader': ['gx84ert'], 'title': 'Stephane Bechtel'}]}
    def create(self, payload, user=None):
        instance_of = self.instance_of
        nodes = []
        try:
            payload = self._validate_and_extract_input(payload)
        except Exception as e:
            logger.warning(str(e))
            return self._format_output([])
        for instance in payload:
            try:
                node = self._create(instance)
                if node:
                    nodes.append(node)
            except Exception as e:
                logger.warning(str(e))
                # return self._format_output([])
        self.post_notification_event(user, nodes, 'c')
        return self._format_output(nodes)

    def post_notification_event(self, actor, instances, action):
        if actor:
            try:
                actor = self._identifier_check(actor)
            except Exception as e:
                logger.info(str(e))
                return None
            else:
                nodes = []
                actor_mbox = self._node_matcher(actor).first()["mbox"]
                actor_title = self._node_matcher(actor).first()["title"]
                if action == 'd':
                    nodes = instances
                else:
                    for instance in instances:
                        instance_id = instance['identifier']
                        instance_title = self._node_matcher(instance_id).first()["title"]
                        class_id = self._get_type(instance_id)
                        class_title = self._get_type(instance_id, title=True)
                        d = {
                            "type_title": class_title,
                            "type_identifier": class_id,
                            "title": instance_title,
                            "identifier": instance_id
                        }
                        nodes.append(d)
                pl = {
                    "payload":[{
                        "actor":{
                            "mbox": actor_mbox,
                            "title": actor_title
                        },
                        "instances": nodes,
                        "action": action
                        }
                    ]
                }
                r = requests.put(self.notify_endpoint, json=pl)
                logger.info('Event notification response: code %s, content: %s' % (str(r.status_code), r.text))
                if r.status_code == 200:
                    return True
        else:
            return None

    # returns a list of email-addresses
    def get_subscribed_users(self):
        subscribers = []
        query = "MATCH (n) WHERE n.subscriber = True return n.mbox"
        result = self.graph.run(query)
        result = result.data()
        if result:
            for d in result:
                subscriber = d['n.mbox']
                if subscriber:
                    subscribers.append(subscriber)
        return subscribers

    def _create(self, instance):
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


    # create helper: creates new node, generates identifier and assignes it
    # to node and returns the identifier of the newly created node
    def _create_node(self, class_id):
        properties = {}
        identifier = self._identifier_generator()
        properties[self.identifier] = identifier
        # create node
        query = "MERGE (s:%s {identifier:{class_id}}) CREATE (i:%s {properties})-[:%s]->(s) RETURN i" % (self.meta, self.model, self.instance_of)
        self.graph.run(query, parameters={"properties": properties,
                                          "class_id": class_id})
        return identifier

    # process required properties in create function
    # This function is destructive (it removes invalid dicts from payload)
    def _check_valid_input_create(self, instance):
        instance_of = self.instance_of
        if instance_of not in instance:
            e = kgexceptions._exception_type_empty(instance)
            logger.warning(str(e))
            return False
        class_identifier = instance[instance_of]
        if not self._is_existant(class_identifier):
            e = kgexceptions._exception_non_existant(str(instance), class_identifier)
            logger.warning(str(e))
            return False
        req_prop = self._get_req_props(class_identifier)
        if self._validate_req_props_create(req_prop, instance):
            return True

    def _validate_req_props_create(self, req_prop, instance):
        for rp in req_prop:
            if rp == self.identifier:
                continue
            if rp not in instance.keys():
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                logger.warning(str(e))
                return False
            elif self._is_empty(instance[rp]):
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                logger.warning(str(e))
                return False
        return True

    # query: execute cypher query (modifying operations excluded)
    # input: MATCH (n{identifier: 'cbd4711') RETURN n.title
    # output: {'payload': [{'n.title': 'Stephane Bechtel'}]}
    def query(self, query):
        try:
            self._validate_query(query)
            # run query
            result = self.graph.run(query)
            result_data = result.data()
            if not result_data:
                e = kgexceptions._exception_cypher(str(query))
                raise e
        except Exception as e:
            logger.warning(str(e))
            return self._format_output([])
        else:
            return self._format_output(result_data)

    # check if query is neither empty or modifying
    def _validate_query(self, query):
        if self._is_empty(query):
            e = kgexceptions._exception_empty()
            raise e
        if self._injection_check(query):
            e = kgexceptions._exception_blacklisted(query)
            raise e

    # is blacklist: checks given query for modifying operations
    def _injection_check(self, query):
        query = query.strip()
        blacklist = self.config['BLACKLIST']
        return any(word in query.lower() for word in blacklist)

    # get: return node's properties and relations by given identifier
    # input: {'payload':[{self.identifier: 54ad929}]}
    # output: {'payload':[{'type': ['cbd4711'], 'member': ['10f6efb'],
    #                     'title': 'Stephane Bechtel', 'familyName': 'Bechtel',
    #                     'givenName': 'Stephane', self.identifier: '54ad929'}]}
    def get(self, payload):
        nodes = []
        try:
            identifiers = self._validate_and_extract_input(payload)
        except Exception as e:
            logger.warning(str(e))
            return self._format_output([])
        for identifier in identifiers:
            try:
                node = self._get_helper(identifier)
                if node:
                    nodes.append(node)
            except Exception as e:
                logger.warning(str(e))
                # return self._format_output([])
        return self._format_output(nodes)


    def _get_helper(self, payload):
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

    def get_instances(self, identifier):
        logger.debug('Running get_instances for id %s' % (identifier))
        result = self.get_self_descendants(identifier)
        instances = self._get_path(result, rel="type", inv=True, degree=-1)

        # format the output for get to accept it
        res_list=[]
        for id in instances:
            res_list.append({self.identifier:id})
        instances = {'payload': res_list}

        instances = self.get(instances)
        return instances

    # update: set new properties and relations to node
    # input: {'payload':[{self.identifier: 'b9c3a6d', 'member':['3b9d007'],
    #                     'familyName': 'Stein'}]}
    # output: {'payload':[{self.identifier: 'b9c3a6d', 'member':['3b9d007'],
    #                      'title': 'Jasmin Stein',
    #                     'givenName': 'Jasmin', 'familyName': 'Stein'}]}]}
    def update(self, payload, user=None):
        nodes = []
        try:
            payload = self._validate_and_extract_input(payload)
        except Exception as e:
            logger.warning(str(e))
            return self._format_output([])
        for instance in payload:
            try:
                node = self._update(instance)
                if node:
                    nodes.append(node)
            except Exception as e:
                logger.warning(str(e))
                # return self._format_output([])
        self.post_notification_event(user, nodes, 'u')
        return self._format_output(nodes)

    def _update(self, instance):
        if self._check_valid_input_update(instance) is not True:
            return None
        instance, identifier = self._delete_shared_items(instance)
        class_id = self._get_type(identifier)
        self._set_attributes(identifier, instance, class_id)
        payload = {self.identifier: identifier}
        node = self._get_helper(payload)
        return node

    def _set_attributes(self, identifier, instance, class_id):
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
                    logger.info(stmt)
        return True

    def _check_valid_input_update(self, instance):
        if self.identifier not in instance:
            e = kgexceptions._exception_non_existant(str(instance), self.identifier)
            logger.warning(str(e))
            return False
        identifier = instance[self.identifier]
        if not self._is_existant(identifier):
            e = kgexceptions._exception_non_existant(str(instance), identifier)
            logger.warning(str(e))
            return False
        class_identifier = self._get_type(identifier)
        req_prop = self._get_req_props(class_identifier)
        for rp in req_prop:
            if rp in instance.keys():
              if self._is_empty(instance[rp]):
                e = kgexceptions._exception_req_prop(str(rp), str(instance))
                logger.warning(str(e))
                return False
        return True

    def _delete_shared_items(self, d):
        identifier = d[self.identifier]
        pl = {self.identifier: identifier}
        node = self._get_helper(pl)
        shared_items = {k: node[k] for k in node if k in d and node[k] == d[k]}
        map(d.pop, shared_items)
        return d, identifier

    # delete: detach ABox-node from its relations and delete it
    # input: {'payload':[{'identifier:' cbd4711}]}
    # output: True
    def delete(self, payload, user=None):
        nodes = []
        instances = []
        try:
            identifiers = self._validate_and_extract_input(payload)
        except Exception as e:
            logger.warning(str(e))
            nodes.append(False)
            return nodes
        else:
            for identifier in identifiers:
                try:
                    pl = self.collect_to_delete_data(identifier['identifier'])
                    node = self._delete_helper(identifier)
                    nodes.append(node)
                    instances.append(pl)
                except Exception as e:
                    logger.warning(str(e))
                    nodes.append(False)
                    # return self._format_output([])
        if instances:
            self.post_notification_event(user, instances, 'd')
        return nodes

    def collect_to_delete_data(self, identifier):
        try:
            instance_title = self._node_matcher(identifier).first()["title"]
            instance_type = self._get_type(identifier)
        except Exception as e:
            raise e
        pl = {
            "title": instance_title,
            "type": instance_type
        }
        return pl

    def _delete_helper(self, payload):
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

    def get_self_descendants(self, identifier):
        result = self._get_path(identifier, rel="subclass_of", inv=True, degree=-1, inc_self=True)
        return result


    def _get_path(self, identifiers, rel, inv, degree=-1, out='identifier', inc_self=False):
        temp_list = []
        if not isinstance(identifiers, list):
            identifiers = [identifiers]
        for identifier in identifiers:
            result = self.__get_path(identifier, rel, inv, degree, out, inc_self)
            temp_list.extend(result)
        return temp_list

    def __get_path(self, identifier, rel, inv, degree=-1, out='identifier', inc_self=False):
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
        else: #omnly one case handled
            query = 'MATCH (n{identifier: {identifier}})%s-[r:%s*%s..]-%s(i) RETURN i.%s' % (left, rel, card, right, out)

        result = self.graph.run(query, parameters={"identifier": identifier})
        result = result.data()
        for d in result:
            for k, v in d.items():
                result_list.append(v)
        return result_list

    # rename to get_val_of_prop
    def get_prop_val(self, identifier, prop_name):
        try:
            node = self._node_matcher(identifier)
            node = node.first()
            prop_val = node[prop_name]
        except:
            prop_val = None
        return prop_val

# ----- private functions (only called internally within this class):

    # _config_parser: json parser for config file
    def _config_parser(self, path=''):
        filename = 'config.yaml'
        filename = path + filename
        with open(filename, 'r') as f:
            self.config = yaml.safe_load(f)

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

        params = self.config['PARAMS']
        for param in params:
            prop = param.keys()[0]
            val = param.values()[0]
            if prop == 'notify_endpoint':
                self.notify_endpoint = val
            if prop == 'parent_logger_name':
                self.parent_logger_name = val


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

    def _is_instance(self, identifier):
        label = ':%s' % self.model
        if self._is_label(identifier, label):
            return True
        else:
            return False

    def _is_class(self, identifier):
        label = ':%s' % self.meta
        if self._is_label(identifier, label):
            return True
        else:
            return False

    def _is_label(self, identifier, label):
        try:
            identifier = self._identifier_check(identifier)
            node = self._node_matcher(identifier).first()
        except Exception as e:
            logger.info(str(e))
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

    def _identifier_check(self, identifier):
        identifier = identifier.strip()
        if not self._is_existant(identifier):
            e = kgexceptions._exception_non_existant(str(identifier))
            raise e
        return identifier

    def _get_type(self, identifier, title=False):
        node = {self.identifier: identifier}
        result = self._get_helper(node)[self.instance_of][0]
        if title:
            node = {self.identifier: result}
            result = self._get_helper(node)['title']
        return result

    def _listify(self, elem):
        if not isinstance(elem, list):
            elem = [elem]
        return elem

    def _create_prop(self, identifier, attr_name, attr_val):
        attr_name = attr_name.lower()
        # Note: attr_name is set differently because py2neo does not
        #       allow to set labels with parameters
        qa = 'MATCH (n) WHERE n.identifier = {identifier} SET n.%s = {attr_val} RETURN n' % attr_name
        # run query for setting properties
        self.graph.run(qa, parameters={"identifier": identifier,
                                       "attr_val": attr_val})

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

    # TODO: rename to _is_valid_property
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

    # TODO: rename to _is_valid_relation
    def _valid_relation(self, sub, rel, obj):
        rel = rel.lower()
        sub_ancestors = self.get_self_ancestors(sub)
        obj_ancestors = self.get_self_ancestors(obj)
        valid_obj = self._get_relation_path(sub_ancestors, rel)
        return any(x in valid_obj for x in obj_ancestors)

    def _get_relation_path(self, identifiers, rel):
        temp_list = []
        if not isinstance(identifiers, list):
            identifiers = [identifiers]
        for identifier in identifiers:
            result = self.__get_relation_path(identifier, rel)
            if not any(x in result for x in temp_list):
                temp_list.extend(result)
        return temp_list

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

    def get_self_ancestors(self, identifier):
        ancestor = self._get_path(identifier, rel="type", inv=False,
                                  degree=-1)
        ancestors = self._get_path(ancestor, rel="subclass_of", inv=False,
                                   degree=-1)
        ancestors.extend(ancestor)
        return ancestors

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
