from py2neo import *
from KgService import *
# from ABox import *
# from TBox import *


with open('_pass.yaml', 'r') as f:
    creds = yaml.safe_load(f)

url = creds['url']
usr = creds['user']
pswd = creds['pass']
path= ''

# abox_service = ABoxService(url, usr, pswd)
# tbox_service = TBoxService(url, usr, pswd)

abox_service = KgService(url, usr, pswd, path)
tbox_service = KgService(url, usr, pswd, path)


def _clear_all(self):
    abox_service.graph.run('MATCH (n:%s) DETACH DELETE n' % 'ABox')

def create(payload):
    return abox_service.create(payload)

def mk_typ(trail):
    return "http://example.org/tbox/" + trail

########### Helper Functions #############

def id(obj):
    return obj["payload"][0]["identifier"]

def mk(item_dict=None):
    if item_dict and type(item_dict) is not list:
        return {"payload":[item_dict]}
    elif item_dict and type(item_dict) is list:
        return {"payload":item_dict}
    else:
        return {"payload":[]}

def tags(type):
    return ["ABox", type]

def mbox(name=""):
    name = name.lower()
    if name == "nasr":
        return "n.k@uni-bamberg.de"
    elif name == "adrian":
        return "a.l@uni-bamberg.de"
    elif name == "daniela":
        return "d.n@uni-bamberg.de"
    else:
        return "monsieur.incognito@uni-bamberg.de"

###############################################

class TestCreate:

    def test_create_nasr(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"
        })
        result = create(payload)

        result_exp = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "mbox": "n.k@uni-bamberg.de",
            "type": [mk_typ("user")],
            "description": "Employee",
            "identifier": id(result),

        })
        assert result == result_exp

        _clear_all(self)

    def test_create_adrian_should_not_create(self):
        payload = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user")
        })
        result = create(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_create_adrian_should_info(self):
        payload = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee",
            "fake": "fake"
        })
        result = create(payload)
        result_exp = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": [mk_typ("user")],
            "description": "Employee",
            "identifier": id(result),

        })
        assert result == result_exp

        _clear_all(self)

    def test_create_monsieur_should_not_create_rel(self):
        payload = mk({
            "type": mk_typ("user"),
            "title": "Monsieur Incognito",
            "description": "Employee",
            "mbox": "m.i@uni-bamberg.de",
            "member": mk_typ("system")
        })
        result = create(payload)
        result_exp = mk({
            "identifier": id(result),
            "type": [mk_typ("user")],
            "title": "Monsieur Incognito",
            "mbox": "m.i@uni-bamberg.de",
            "description": "Employee",

        })
        assert result == result_exp

        _clear_all(self)

    def test_create_daniela_set_labels(self):
        payload = mk({
            "title": "Prof DN",
            "type": mk_typ("user"),
            "description": "Professor",
            "mbox": "d.n@uni-bamberg.de",

        })
        result = create(payload)
        result_exp = mk({
            "identifier": id(result),
            "type": [mk_typ("user")],
            "title": "Prof DN",
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"
        })
        assert result == result_exp

        _clear_all(self)

    # def test_create_multiple(self):
    #     payload = mk([
    #         {"title": "Prof DN",
    #         "type": mk_typ("user"),
    #         "mbox": "d.n@uni-bamberg.de",
    #         "description": "Professor"}
    #         ])
    #     daniela = create(payload)
    #     payload = mk([
    #         {"title": "Mr AL",
    #          "mbox": "a.l@uni-bamberg.de",
    #         "type": mk_typ("user"),
    #         "description": "Employee"},
    #         {"title": "Mr NK",
    #         "mbox": "n.k@uni-bamberg.de",
    #         "type": mk_typ("user"),
    #         "description": "Employee"},
    #     ])
    #     result = create(payload, id(daniela))
    #     result_exp = mk([
    #         {"title": "Mr AL",
    #         "identifier": id(result),
    #         "type": [mk_typ("user")],
    #         "mbox": "a.l@uni-bamberg.de",
    #         "description": "Employee"},
    #         {"title": "Mr NK",
    #         "mbox": "n.k@uni-bamberg.de",
    #         "identifier": result["payload"][1]["identifier"],
    #         "type": [mk_typ("user")],
    #         "description": "Employee"},
    #     ])
    #     assert result == result_exp

    def test_create_multiple_one_fails(self):
        payload = mk([
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"},
            {"title": "Mr AL",
             "mbox": "a.l@uni-bamberg.de",
            # "type": mk_typ("user"),
            "description": "Employee"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
        ])
        result = create(payload)
        result_exp = mk([
            {"title": "Prof DN",
            "identifier": id(result),
            "type": [mk_typ("user")],
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "identifier": result["payload"][1]["identifier"],
            "type": [mk_typ("user")],
            "description": "Employee"},
        ])
        assert result == result_exp

        _clear_all(self)

    def test_create_invalid_label_should_fail(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"
        })
        result = create(payload)
        result_exp = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "mbox": "n.k@uni-bamberg.de",
            "type": [mk_typ("user")],
            "description": "Employee",
            "identifier": id(result)
        })
        assert result == result_exp

        _clear_all(self)

    def test_create_valid_rel(self):
        payload = mk(
            {"title": "Mr NK",
            "type": mk_typ("user"),
            "mbox": mbox("nasr"),
            "description": "Employee"}
        )
        nasr = create(payload)
        payload = mk({
            "title": "Future IOT",
            "type": mk_typ("project"),
            "description": "Research Project",
            "member" : id(nasr)
            }
            )
        result = create(payload)
        result_exp = mk({
            "title": "Future IOT",
            "type": [mk_typ("project")],
            "description": "Research Project",
            "member": [id(nasr)],
            "identifier": id(result)
        })
        assert result == result_exp

        _clear_all(self)

    def test_create_invalid_type_should_fail(self):
        payload = mk({
            "title": "Adrian",
            "mbox" : mbox("adrian"),
            "type": mk_typ("fake"),
            "description": "Employee"}
            )
        result = create(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_create_empty_req_prop_should_fail(self):
        payload = mk({
            "title": "Adrian",
            "mbox" : mbox("adrian"),
            "type": mk_typ("user"),
            "description": ""}
            )
        result = create(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_create_given_id_should_skip(self):
        payload = mk({
            "title": "Adrian",
            "mbox" : mbox("adrian"),
            "type": mk_typ("user"),
            "identifier": "http://example.org/abox/aef8b9b4-4267-f4f0d5754bd2",
            "description": "Developer"}
            )
        result = create(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

class TestGetAttributes:

    def test_get_attributes_user(self):
        class_uri = mk_typ('user')
        result = tbox_service.get_attributes(class_uri)
        result_exp = ['mbox',
                      'description',
                      'identifier',
                      'title',
                      'subscriber',
                      'familyname',
                      'givenname',
                      'contributor',
                      'rightsholder',
                      'rights',
                      'haspart',
                      'relation',
                      'references'
                      ]
        assert result == result_exp

        _clear_all(self)


class TestGetAttType:

    def test_get_att_type_prop(self):
        title = 'mbox'
        result = tbox_service.get_att_type(title)
        result_exp = 'xsd:string'
        assert result == result_exp

        _clear_all(self)

    def test_get_att_type_identifier(self):
        title = 'identifier'
        result = tbox_service.get_att_type(title)
        result_exp = 'identifier'
        assert result == result_exp

        _clear_all(self)

    def test_get_att_type_instance_of(self):
        title = 'type'
        result = tbox_service.get_att_type(title)
        result_exp = 'type'
        assert result == result_exp

        _clear_all(self)

    def test_get_att_type_relation(self):
        title = 'contributor'
        result = tbox_service.get_att_type(title)
        result_exp = 'ref Agent'
        assert result == result_exp

        _clear_all(self)


class TestGetPropVal:

    def test_get_prop_val_kbms(self):
        id = mk_typ('kbmsthing')
        print("ID: ", id)
        prop_name = 'title'
        result = tbox_service.get_prop_val(id, prop_name)
        result_exp = 'KBMSThing'
        assert result == result_exp

        _clear_all(self)

    def test_get_prop_val_abox(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"
        })
        nk = create(payload)
        id = nk['payload'][0]['identifier']
        prop_name = 'mbox'
        result = tbox_service.get_prop_val(id, prop_name)
        result_exp = 'n.k@uni-bamberg.de'
        assert result == result_exp

        _clear_all(self)

    def test_get_prop_val_kbms_should_fail(self):
        id = mk_typ('kbmsthing')
        prop_name = 'titel'
        result = tbox_service.get_prop_val(id, prop_name)
        result_exp = None
        assert result == result_exp

        _clear_all(self)

class TestGet:

    def test_get_nasr(self):
        payload = mk({
            "title": "Mr NK",
            "type": mk_typ("user"),
            "mbox" : mbox("nasr"),
            "description": "Employee"
        })
        nasr = create(payload)
        result = abox_service.get(nasr)
        assert nasr == result

        _clear_all(self)

    def test_get_project(self):
        payload = mk({
            "title": "Mr NK",
            "type": mk_typ("user"),
            "mbox" : mbox("nasr"),
            "description": "Employee"
        })
        nasr = create(payload)
        payload = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"
        })
        adrian = create(payload)
        payload = mk({
            "title": "Simutool Project",
            "type": mk_typ("project"),
            "member": [id(adrian), id(nasr)],
            "description": "Research Project"
        })
        st = create(payload)
        result = abox_service.get(st)
        assert st == result

        _clear_all(self)

    def test_get_empty_id_should_fail(self):
        payload = mk({
            "identifier": ""
        })
        result = abox_service.get(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)


class TestUpdate:

    def test_update_nasr(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": mk_typ("user"),
            "mbox": "n.k@uni-bamberg.de",
            "description": "Employee"
        })
        nasr = create(payload)
        payload = mk({
            "identifier": id(nasr),
            "description": "Development Lead"
        })
        result = abox_service.update(payload)
        result_exp = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": [mk_typ("user")],
            "description": "Development Lead",
            "identifier": id(nasr),
            "mbox": "n.k@uni-bamberg.de"
        })
        assert result == result_exp

        _clear_all(self)

    def test_update_adrian_should_fail(self):
        payload = mk({
            "title": "Mr AL",
            "givenname": "Adrian",
            "type": mk_typ("user"),
            "mbox": "a.l@uni-bamberg.de",
            "description": "Employee"
        })
        adrian = create(payload)
        payload = mk({
            # "identifier": id(adrian),
            "title": "Mr AL",
            "description": "Development Arm"
        })
        result = abox_service.update(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_update_multiple_one_fails(self):
        payload = {"payload":[
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"},
            {"title": "Mr AL",
            "type": mk_typ("user"),
            "mbox": "a.l@uni-bamberg.de",
            "description": "Employee"},
            {"title": "Mr NK",
            "type": mk_typ("user"),
            "mbox": "n.k@uni-bamberg.de",
            "description": "Employee"},
        ]}
        nodes = create(payload)
        payload = {"payload":[
            {"identifier": id(nodes),
            "description": "Professor1"},
            {
            "description": "Employee1"},
            {"identifier": nodes["payload"][2]["identifier"],
            "description": "Employee2"},
        ]}
        result = abox_service.update(payload)
        result_exp = {"payload":[
            {"identifier": id(nodes),
            "type": [mk_typ("user")],
            "description": "Professor1",
            "mbox": "d.n@uni-bamberg.de",
            "title": "Prof DN"},
            {"identifier": nodes["payload"][2]["identifier"],
            "type": [mk_typ("user")],
            "description": "Employee2",
            "mbox": "n.k@uni-bamberg.de",
            "title": "Mr NK"}
        ]}
        assert result == result_exp

        _clear_all(self)

    def test_update_valid_rel(self):
        payload = {"payload":[
            {"title": "Future IOT",
            "type": mk_typ("project"),
            "description": "Research Project"},
            {"title": "Simutool Project",
            "type": mk_typ("project"),
            "description": "Research Project"}
        ]}
        projects = create(payload)
        payload = mk(
            {"identifier": id(projects),
            "relation": projects["payload"][1]["identifier"]}
        )
        result = abox_service.update(payload)
        result_exp = {"payload":[
            {"description": "Research Project",
            "title": "Future IOT",
            "identifier": id(result),
            "type": [mk_typ("project")],
            "relation": [projects["payload"][1]["identifier"]]}
        ]}
        assert result == result_exp

        _clear_all(self)

    def test_update_invalid_attr_should_fail(self):
        payload = mk(
            {"title": "Future IOT",
            "type": mk_typ("project"),
            "description": "Research Project"})
        project = create(payload)
        payload = mk(
            {"identifier": id(project),
            "fake": "Testing"}
        )
        result = abox_service.update(payload)
        result_exp = mk(
            {"description": "Research Project",
            "title": "Future IOT",
            "identifier": id(result),
            "type": [mk_typ("project")]})
        assert result == result_exp

        _clear_all(self)

    def test_update_empty_id_should_fail(self):
        payload = mk(
            {"identifier": "",
            "description": "Testing"}
        )
        result = abox_service.update(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_update_empty_req_prop_should_fail(self):
        payload = mk(
            {"title": "Future IOT",
            "type": mk_typ("project"),
            "description": "Research Project"})
        project = create(payload)
        payload = mk(
            {"identifier": id(project),
            "description": ""}
        )
        result = abox_service.update(payload)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)


class TestQuery:

    def test_query(self):
        payload = mk({
            "title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"
        })
        result = create(payload)
        query = "MATCH (n{mbox: 'n.k@uni-bamberg.de'}) RETURN n.title"
        result = abox_service.query(query)
        result_exp = mk({"n.title": "Mr NK"})
        assert result == result_exp

        _clear_all(self)

    def test_query_should_fail(self):
        query = "MATCH (n) RETURN m"
        result = abox_service.query(query)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_query_no_results_should_fail(self):
        query = "MATCH (n:FBox) RETURN n"
        result = abox_service.query(query)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)

    def test_query_empty_should_fail(self):
        query = ""
        result = abox_service.query(query)
        result_exp = None
        assert result == mk()

        _clear_all(self)

    def test_query_blacklisted_should_fail(self):
        query = "MATCH (n) DETACH DELETE n"
        result = abox_service.query(query)
        result_exp = mk()
        assert result == result_exp

        _clear_all(self)


class TestDelete:

    def test_delete_nasr(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "n.k@uni-bamberg.de"
        })
        nasr = create(payload)
        payload = mk({
            "identifier": id(nasr)
        })
        result = abox_service.delete(payload)
        result_exp = [True]
        assert result == result_exp

        _clear_all(self)

    def test_delete_empty_should_fail(self):
        payload = mk()
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

        _clear_all(self)

    def test_delete_empty_id_should_fail(self):
        payload = mk({})
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

        _clear_all(self)

    def test_delete_multiple(self):
        payload = mk([
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"},
            {"title": "Mr AL",
             "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
        ])
        mobi = create(payload)
        payload = mk([
            {"identifier": id(mobi)},
            {"identifier": mobi["payload"][1]["identifier"]},
            {"identifier": mobi["payload"][2]["identifier"]}
        ])
        result = abox_service.delete(payload)
        result_exp = [True, True, True]
        assert result == result_exp

        _clear_all(self)

    def test_delete_multiple_one_fails(self):
        payload = mk([
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"},
            {"title": "Mr AL",
             "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
        ])
        mobi = create(payload)
        payload = mk([
            {"identifier": id(mobi)},
            {"identifier": "identifier"},
            {"identifier": mobi["payload"][2]["identifier"]}
        ])
        result = abox_service.delete(payload)
        result_exp = [True, False, True]
        assert result == result_exp

        _clear_all(self)

    def test_delete_one_fails(self):
        payload = mk([
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"}])
        mobi = create(payload)
        payload = mk([{"identifier": "identifier"}])
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

        _clear_all(self)


    def test_delete_missing_pl_should_fail(self):
        payload = {"identifier":"fake"}
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

        _clear_all(self)

    def test_delete_tbox_should_fail(self):
        payload = mk(
            {"identifier": mk_typ("project")}
        )
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

        _clear_all(self)

class TestInternals:

    def test_is_instance(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "n.k@uni-bamberg.de",
            "subscriber": True
        })
        self.nasr = create(payload)
        pl = id(self.nasr)
        result = abox_service._is_instance(pl)
        result_exp = True
        assert result == result_exp

        _clear_all(self)


    def test_is_instance_should_fail(self):
        pl = mk_typ("user")
        result = abox_service._is_instance(pl)
        result_exp = False
        assert result == result_exp

        _clear_all(self)

    def test_is_instance_should_fail2(self):
        pl = mk_typ("user2")
        result = abox_service._is_instance(pl)
        result_exp = False
        assert result == result_exp

        _clear_all(self)

    def test_is_class(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "n.k@uni-bamberg.de",
            "subscriber": True
        })
        self.nasr1 = create(payload)
        pl = id(self.nasr1)
        result = abox_service._is_class(pl)
        result_exp = False
        assert result == result_exp

        _clear_all(self)

    def test_is_class_should_fail(self):
        pl = mk_typ("user")
        result = abox_service._is_class(pl)
        result_exp = True
        assert result == result_exp

        _clear_all(self)

    def test_is_class_should_fail2(self):
        pl = mk_typ("user2")
        result = abox_service._is_class(pl)
        result_exp = False
        assert result == result_exp

        _clear_all(self)

    # def test_get_subscribed_users(self):
    #     payload = mk({
    #         "title": "Mr NK",
    #         "type": mk_typ("user"),
    #         "description": "Employee",
    #         "mbox": "n.k@uni-bamberg.de",
    #         "subscriber": True
    #     })
    #     node = create(payload)
    #     result = abox_service.get_subscribed_users()
    #     result_exp = 1
    #     assert len(result) == result_exp
    #
    #     _clear_all(self)

    # def test_post_notification_event(self):
    #     payload = mk({
    #         "title": "Mr NK",
    #         "givenname": "N.",
    #         "type": mk_typ("user"),
    #         "description": "Employee",
    #         "mbox": "n.k@uni-bamberg.de",
    #         "subscriber": True
    #     })
    #     self.nasr = create(payload)
    #     payload = mk({
    #         "title": "Mr AL",
    #         "givenname": "Adrian",
    #         "type": mk_typ("user"),
    #         "description": "Employee",
    #         "mbox": "a.l@uni-bamberg.de",
    #         "subscriber": True
    #     })
    #     actor = id(self.nasr)
    #     result = abox_service.create(payload, actor)
    #     result_exp = mk({
    #         "title": "Mr AL",
    #         "mbox": "a.l@uni-bamberg.de",
    #         "type": [mk_typ("user")],
    #         "description": "Employee",
    #         "identifier": id(result),
    #         "givenname": "Adrian",
    #         "subscriber": True
    #     })
    #     assert result == result_exp

    def test_post_notification_event_invalid_actor(self):
        payload = mk({
            "title": "Mr AL",
            "givenname": "Adrian",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "a.l@uni-bamberg.de",
            "subscriber": True
        })
        actor = 'http://example.org/invalid'
        result = abox_service.create(payload, actor)
        result_exp = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": [mk_typ("user")],
            "description": "Employee",
            "identifier": id(result),
            "givenname": "Adrian",
            "subscriber": True
        })
        assert result == result_exp

        _clear_all(self)

    def test_get_tbox_node_by_title(self):
        class_title = "User"
        prop_name = None
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp = mk({
            'html_info': '',
            'description': 'People that create knowledge and have an account',
            'title': 'User',
            # 'namespace':'',
            'admin': 'yes',
            'optional_property': ['http://example.org/tbox/subscriber'],
            'ontology_level': 'upper',
            'version': 'v3.2',
            'subclass_of': ['http://example.org/tbox/person'],
            'sing': 'User',
            'identifier': 'http://example.org/tbox/user',
            'required_property': ['http://example.org/tbox/mbox'],
            'pl': 'Users'
        })
        assert result == result_exp

        _clear_all(self)

    def test_get_tbox_node_by_title_prop(self):
        class_title = "user"
        prop_name = 'description'
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp =  'People that create knowledge and have an account'
        assert result == result_exp

        _clear_all(self)

    def test_get_tbox_node_by_title_prop_invalid_class(self):
        class_title = "user2"
        prop_name = 'description'
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp = None
        assert result == result_exp

        _clear_all(self)

class TestGetInstances:

    def test_get_instances(self):
        payload = mk({
            "title": "Mr NK",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "n.k@uni-bamberg.de",
            "subscriber": True
        })
        node = create(payload)
        class_id = mk_typ('user')
        result = tbox_service.get_instances(class_id)
        assert result == node

        _clear_all(self)

class TestGetPath:

    def test_get_path(self):
        identifier = mk_typ('user')
        rel = "subclass_of"
        inv = False
        inc_self = False

        result = tbox_service._get_path(identifier, rel, inv,  inc_self)
        result_exp = [
            'http://example.org/tbox/person',
            'http://example.org/tbox/agent',
            'http://example.org/tbox/kbmsthing'
        ]
        assert result == result_exp

        _clear_all(self)
