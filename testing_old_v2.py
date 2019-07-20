from py2neo import *
from KgService import *
from TBox import *


tbox_service = TBoxService("http://127.0.0.1:7474/db/data/","neo4j", "pass", model='ABox', meta='TBox')
tbox_base_uri = 'http://example.org/tbox/'

class TestCreate:

    def test_create_nasr(self):
        payload = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'
        }]}
        result = self.tbox_service.create(payload, type_as_tag=True)
        result_exp = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee',
            'identifier': result['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
        }]}
        assert result == result_exp


    def test_create_adrian_should_not_create(self):
        payload = {'payload':[{
            'title': 'Mr AL',
            'type': self.tbox_base_uri + 'user'
        }]}
        result = self.tbox_service.create(payload)
        result_exp = payload = {'payload':[]}
        assert result == result_exp


    def test_create_adrian_should_info(self):
        payload = {'payload':[{
            'title': 'Mr AL',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee',
            'fake': 'fake'
        }]}
        result = self.tbox_service.create(payload)
        result_exp = {'payload':[{
            'title': 'Mr AL',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee',
            'identifier': result['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
        }]}
        assert result == result_exp

    def test_create_monsieur_should_not_create_rel(self):
        payload = {'payload':[{
            'type': self.tbox_base_uri + 'user',
            'title': 'Monsieur Incognito',
            'description': 'Employee',
            'member': self.tbox_base_uri + 'system'
        }]}
        result = self.tbox_service.create(payload)
        result = result
        result_exp = {'payload':[{
            'identifier': result['payload'][0]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'title': 'Monsieur Incognito',
            'description': 'Employee',
            'tags': ['ABox', 'user'],
        }]}
        assert result == result_exp

    def test_create_daniela_set_labels(self):
        payload = {'payload':[{
            'title': 'Prof DN',
            'type': self.tbox_base_uri + 'user',
            'description': 'Professor',
            'tags': ['Tag1', 'Tag2']
        }]}
        result = self.tbox_service.create(payload, test_as_tag=True)
        result_exp = {'payload':[{
            'identifier': result['payload'][0]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'title': 'Prof DN',
            'description': 'Professor',
            'tags': ['ABox', 'test', 'user', 'tag2', 'tag1']
        }]}
        assert result == result_exp


    def test_create_multiple_one_fails(self):
        payload = {'payload':[
            {'title': 'Prof DN',
            'type': self.tbox_base_uri + 'user',
            'description': 'Professor'},
            {'title': 'Mr AL',
            # 'type': self.tbox_base_uri + 'user',
            'description': 'Employee'},
            {'title': 'Mr NK',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'},
        ]}
        result = self.tbox_service.create(payload, test_as_tag=True)
        result_exp = {'payload':[
            {'title': 'Prof DN',
            'identifier': result['payload'][0]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'tags': ['ABox', 'test', 'user'],
            'description': 'Professor'},
            {'title': 'Mr NK',
            'identifier': result['payload'][1]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'tags': ['ABox', 'test', 'user'],
            'description': 'Employee'},
        ]}
        assert result == result_exp

    def test_create_invalid_label_should_fail(self):
        payload = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee',
            'tags': ['vali-de']
        }]}
        result = self.tbox_service.create(payload, type_as_tag=True)
        result_exp = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee',
            'identifier': result['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
        }]}
        assert result == result_exp

    def test_create_valid_rel(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}
            ]}
        future_iot = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'title': 'Mr NK',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee',
            'member': future_iot['payload'][0]['identifier']}
            ]}
        result = self.tbox_service.create(payload, type_as_tag=True)
        result_exp = {'payload':[{
            'title': 'Mr NK',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee',
            'identifier': result['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
            'member': [future_iot['payload'][0]['identifier']]
        }]}
        assert result == result_exp

    def test_create_invalid_type_should_fail(self):
        payload = {'payload':[
            {'title': 'Adrian',
            'type': self.tbox_base_uri + 'fake',
            'description': 'Employee'}
            ]}
        result = self.tbox_service.create(payload, type_as_tag=True)
        result_exp = {'payload':[]}
        assert result == result_exp

    def test_create_empty_req_prop_should_fail(self):
        payload = {'payload':[
            {'title': 'Adrian',
            'type': self.tbox_base_uri + 'user',
            'description': ''}
            ]}
        result = self.tbox_service.create(payload, type_as_tag=True)
        result_exp = {'payload':[]}
        assert result == result_exp


        self.tbox_service._clear_all()


class TestGet:

    def test_get_multi_rel_of_type(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'},
            {'title': 'Simutool Project',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}
            ]}
        projects = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[{
            'title': 'Mr NK',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee',
            'member': [projects['payload'][0]['identifier'],
                        projects['payload'][0]['identifier']]
        }]}
        nasr = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': nasr['payload'][0]['identifier']}
        ]}
        result = self.tbox_service.get(payload)
        result_exp = {'payload':[{
            'title': 'Mr NK',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee',
            'identifier': nasr['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
            'member': [projects['payload'][0]['identifier'],
                        projects['payload'][0]['identifier']]
        }]}
        assert result == result_exp


    def test_get_project(self):
        payload = {'payload':[
            {'identifier': 'http://example.org/tbox/project'}
        ]}
        result = self.tbox_service.get(payload)
        result_exp = {'payload': [
            {'subclass_of': [self.tbox_base_uri + 'activity'],
            'identifier': self.tbox_base_uri + 'project',
            'description': 'An undertaking requiring concerted effort by Agents',
            'version': '3.2',
            'tags': ['TBox'],
            'title': 'Project'}]}
        assert result == result_exp


    def test_create_daniela_check_labels(self):
        payload = {'payload':[{
            'title': 'Prof DN',
            'type': self.tbox_base_uri + 'user',
            'description': 'Professor'
        }]}
        daniela = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': daniela['payload'][0]['identifier']}
        ]}
        result = self.tbox_service.get(payload)
        result_exp = {'payload': [{
            'identifier': daniela['payload'][0]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Professor',
            'tags': ['ABox', 'user'],
            'title': 'Prof DN'
            }]}
        assert result == result_exp


    def test_get_empty_id_should_fail(self):
        payload = {'payload':[
            {'identifier': ''}
        ]}
        result = self.tbox_service.get(payload)
        result_exp = {'payload': []}
        assert result == result_exp

        self.tbox_service._clear_all()


class TestUpdate:


    def test_update_nasr(self):
        payload = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'
        }]}
        nasr = self.tbox_service.create(payload)
        payload = {'payload':[{
            'identifier': nasr['payload'][0]['identifier'],
            'description': 'Development Lead'
        }]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Development Lead',
            'identifier': nasr['payload'][0]['identifier'],
            'tags': ['ABox', 'user'],
        }]}
        assert result == result_exp


    def test_update_multiple_one_fails(self):
        payload = {'payload':[
            {'title': 'Prof DN',
            'type': self.tbox_base_uri + 'user',
            'description': 'Professor'},
            {'title': 'Mr AL',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'},
            {'title': 'Mr NK',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'},
        ]}
        nodes = self.tbox_service.create(payload)
        payload = {'payload':[
            {'identifier': nodes['payload'][0]['identifier'],
            'description': 'Professor1'},
            {
            'description': 'Employee1'},
            {'identifier': nodes['payload'][2]['identifier'],
            'description': 'Employee2'},
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': [
            {'identifier': nodes['payload'][0]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Professor1',
            'tags': ['ABox', 'user'],
            'title': 'Prof DN'},
            {'identifier': nodes['payload'][2]['identifier'],
            'type': [self.tbox_base_uri + 'user'],
            'description': 'Employee2',
            'tags': ['ABox', 'user'],
            'title': 'Mr NK'}
        ]}
        assert result == result_exp


    def test_labels(self):
        payload = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'
        }]}
        nasr = self.tbox_service.create(payload)
        identifier = nasr['payload'][0]['identifier']
        node = self.tbox_service._node_matcher(identifier)
        node = node.first()
        node.add_label("label")


    def test_update_valid_rel(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'},
            {'title': 'Simutool Project',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}
            ]}
        projects = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': projects['payload'][0]['identifier'],
            'related': projects['payload'][0]['identifier']}
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': [
        {'tags': ['ABox', 'project'],
        'description': 'Research Project',
        'title': 'Future IOT',
        'identifier': result['payload'][0]['identifier'],
        'type': [self.tbox_base_uri + 'project'],
        'related': [projects['payload'][0]['identifier']]}]}
        assert result == result_exp


    def test_update_tags(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}]}
        project = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': project['payload'][0]['identifier'],
            'tags': 'Testing'}
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': [
        {'tags': ['ABox', 'project', 'testing'],
        'description': 'Research Project',
        'title': 'Future IOT',
        'identifier': result['payload'][0]['identifier'],
        'type': [self.tbox_base_uri + 'project']}]}
        assert result == result_exp


    def test_update_invalid_attr_should_fail(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}]}
        project = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': project['payload'][0]['identifier'],
            'fake': 'Testing'}
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': [
        {'tags': ['ABox', 'project'],
        'description': 'Research Project',
        'title': 'Future IOT',
        'identifier': result['payload'][0]['identifier'],
        'type': [self.tbox_base_uri + 'project']}]}
        assert result == result_exp


    def test_update_empty_id_should_fail(self):
        payload = {'payload':[
            {'identifier': '',
            'description': 'Testing'}
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': []}
        assert result == result_exp


    def test_update_empty_req_prop_should_fail(self):
        payload = {'payload':[
            {'title': 'Future IOT',
            'type': self.tbox_base_uri + 'project',
            'description': 'Research Project'}]}
        project = self.tbox_service.create(payload, type_as_tag=True)
        payload = {'payload':[
            {'identifier': project['payload'][0]['identifier'],
            'description': ''}
        ]}
        result = self.tbox_service.update(payload)
        result_exp = {'payload': []}
        assert result == result_exp

        self.tbox_service._clear_all()


class TestQuery:


    def test_count_query(self):
        query = "MATCH (n{identifier: 'http://example.org/tbox/project'})RETURN count(n)"
        result = self.tbox_service.query(query)
        result_exp = {'payload': [{'count(n)': 1}]}
        assert result == result_exp


    def test_query(self):
        query = "MATCH (n{identifier: 'http://example.org/tbox/project'})RETURN n.identifier"
        result = self.tbox_service.query(query)
        result_exp = {'payload': [{'n.identifier': self.tbox_base_uri + 'project'}]}
        assert result == result_exp



    def test_query_should_fail(self):
        query = "MATCH (n) RETURN m"
        result = self.tbox_service.query(query)
        result_exp = None
        assert result == result_exp

    def test_query_no_results_should_fail(self):
        query = "MATCH (n:FBox) RETURN n"
        result = self.tbox_service.query(query)
        result_exp = None
        assert result == result_exp

    def test_query_empty_should_fail(self):
        query = ""
        result = self.tbox_service.query(query)
        result_exp = None
        assert result == result_exp

    def test_query_blacklisted_should_fail(self):
        query = "MATCH (n) DETACH DELETE n"
        result = self.tbox_service.query(query)
        result_exp = None
        assert result == result_exp


        self.tbox_service._clear_all()


class TestDelete:


    def test_delete_nasr(self):
        payload = {'payload':[{
            'title': 'Mr NK',
            'givenName': 'N.',
            'type': self.tbox_base_uri + 'user',
            'description': 'Employee'
        }]}
        nasr = self.tbox_service.create(payload)
        payload = {'payload':[{
            'identifier': nasr['payload'][0]['identifier']
        }]}
        result = self.tbox_service.delete(payload)
        result_exp = [True]
        assert result == result_exp


    def test_delete_empty_should_fail(self):
        payload = {'payload':[]}
        result = self.tbox_service.delete(payload)
        result_exp = None
        assert result == result_exp


    def test_delete_empty_id_should_fail(self):
        payload = {'payload':[{}]}
        result = self.tbox_service.delete(payload)
        result_exp = None
        assert result == result_exp


    def test_delete_empty_pl_should_fail(self):
        payload = {}
        result = self.tbox_service.delete(payload)
        result_exp = None
        assert result == result_exp


    def test_delete_missing_pl_should_fail(self):
        payload = {'identifier':'fake'}
        result = self.tbox_service.delete(payload)
        result_exp = None
        assert result == result_exp

    def test_delete_tbox_should_fail(self):
        payload = {'payload':[{
            'identifier': self.tbox_base_uri + 'project'
        }]}
        result = self.tbox_service.delete(payload)
        result_exp = None
        assert result == result_exp

        self.tbox_service._clear_all()
