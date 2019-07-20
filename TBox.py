from abc import ABCMeta, abstractmethod
from KgService import *

class TBoxService (KgService):
    base_url = "http://example.org/tbox/"
    def __init__(self, url, user, pwd, path=''):
        super(TBoxService, self).__init__(url, user, pwd, model='TBox', meta='M', path=path)


    def get_model_label(self):
        return "TBox"


    def get_subtypes(self, class_identifier, direct_children, include_self):

    	"""
    		Given a class identifier returns all the decendants of the Node.

    		Inputs:
    			class_identifier string identifier of the class to be queiried
    			direct_children a boolean that defaults to False if not specified. If set to true only returns the direct children of class_identifier, otherwise all the decendants
    			include_self a boolean that defaults to True if not specified. If True it includes the node class_identifier in the returned data, otherwise class_identifier node is omited
    		Outputs:
    			The usual payload
                 {'payload':[{'title': 'Stephane Bechtel', 'familyName': 'Bechtel',
                              'givenName': 'Stephane', 'identifier': '54ad929'},
                             {'title': 'Mo Abas', ...}, ...]}
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
    		Takes a class uri a retuns a list of the names of all the properties and relations of that class

            Inputs:
                class_uri string uri of the class to be queiried
            Outputs:
                A list of strings of the names of all properties and relations:
                Ex. ['title', 'description', 'type', 'identifier', 'rightsholder']
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

    # Just for TBox (schema-related)
    def get_att_type(self, att_title):
        """
        A function that takes a string name of a property or relationship and returns its type

        `get_att_type(att_title) -> string`

        There are 4 cases:
        *  if att_title equals the value of `self.identifier` return `'identifier'`
        *  if att_title equals the value of `self.instance_of` return `'type'`
        *  if att_title is the title of a relation that points to class with title `class_xyz`, return `ref class_xyz`
        *  if att_title is the title of a property, return the value of the field 'xsd_type' of that property (ex. `xsd:string` )
        KgService.register(TBoxService)
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
                logger.info(str(e))
            try:
                matcher = RelationshipMatcher(self.graph)
                rel = matcher.match(title=att_title)
                rel = rel.first()
                if rel:
                    end_node = rel.end_node
                    att_type = 'ref ' + str(end_node['title'])
            except Exception as e:
                logger.info(str(e))
        return att_type

    # if prop_name is None returns a payload in the agreed format
    # else it returns just the value of the attribute, or None
    def _get_tbox_node_by_title(self, class_title, prop_name=None):
        #TODO : This must be queried by title, and not constructed,
        #       this is because urls can be generated differently in future.
        class_id = self.base_url + str(class_title)
        try:
            class_id = self._identifier_check(class_id)
            payload = {self.identifier: class_id}
            node = self._get_helper(payload)
        except Exception as e:
            logger.info(str(e))
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
