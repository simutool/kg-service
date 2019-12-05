from KgService import *

class KgSchemaService (KgService):
    def __init__(self, url, user, pwd, path=''):
        super(KgSchemaService, self).__init__(url, user, pwd, path=path)
        self.model='TBox'
        self.meta='M'

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
    def _get_node_by_title(self, class_title, prop_name=None):
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


KgService.register(KgSchemaService)