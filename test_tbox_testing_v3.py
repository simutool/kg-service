from py2neo import *
from KgService import *
from ABox import *
from TBox import *

abox_service = ABoxService("http://141.13.162.157:7674", "neo4j", "neo6j")
tbox_service = TBoxService("http://141.13.162.157:7674", "neo4j", "neo6j")

tbox_base_uri = "http://example.org/tbox/"

def create(payload):
    return abox_service.create(payload)

def mk_typ(trail):
    return tbox_base_uri + trail

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

    def test_create_adrian_should_not_create(self):
        payload = mk({
            "title": "Mr AL",
            "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user")
        })
        result = create(payload)
        result_exp = mk()
        assert result == result_exp


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

    def test_create_multiple(self):
        payload = mk([
            {"title": "Prof DN",
            "type": mk_typ("user"),
            "mbox": "d.n@uni-bamberg.de",
            "description": "Professor"}
            ])
        daniela = create(payload)
        payload = mk([
            {"title": "Mr AL",
             "mbox": "a.l@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "type": mk_typ("user"),
            "description": "Employee"},
        ])
        result = abox_service.create(payload, id(daniela))
        result_exp = mk([
            {"title": "Mr AL",
            "identifier": id(result),
            "type": [mk_typ("user")],
            "mbox": "a.l@uni-bamberg.de",
            "description": "Employee"},
            {"title": "Mr NK",
            "mbox": "n.k@uni-bamberg.de",
            "identifier": result["payload"][1]["identifier"],
            "type": [mk_typ("user")],
            "description": "Employee"},
        ])
        assert result == result_exp

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

    def test_create_given_id_should_skip(self):
        payload = mk({
            "title": "Adrian",
            "mbox" : mbox("adrian"),
            "type": mk_typ("user"),
            "identifier": "http://example.org/abox/aef8b9b4-4267-4702-a093-f4f0d5754bd2",
            "description": "Developer"}
            )
        result = create(payload)
        result_exp = mk()
        assert result == result_exp

        abox_service._clear_all()

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


class TestGetAttType:

    def test_get_att_type_prop(self):
        title = 'mbox'
        result = tbox_service.get_att_type(title)
        result_exp = 'xsd:string'
        assert result == result_exp

    def test_get_att_type_identifier(self):
        title = 'identifier'
        result = tbox_service.get_att_type(title)
        result_exp = 'identifier'
        assert result == result_exp

    def test_get_att_type_instance_of(self):
        title = 'type'
        result = tbox_service.get_att_type(title)
        result_exp = 'type'
        assert result == result_exp

    def test_get_att_type_relation(self):
        title = 'contributor'
        result = tbox_service.get_att_type(title)
        result_exp = 'ref Agent'
        assert result == result_exp


class TestGetPropVal:

    def test_get_prop_val_kbms(self):
        id = mk_typ('kbmsthing')
        prop_name = 'title'
        result = tbox_service.get_prop_val(id, prop_name)
        result_exp = 'KBMSThing'
        assert result == result_exp

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

    def test_get_prop_val_kbms_should_fail(self):
        id = mk_typ('kbmsthing')
        prop_name = 'titel'
        result = tbox_service.get_prop_val(id, prop_name)
        result_exp = None
        assert result == result_exp

        abox_service._clear_all()

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
    #     payload = mk({
    #         "title": "Mr AL",
    #         "mbox": "a.l@uni-bamberg.de",
    #         "type": mk_typ("user"),
    #         "description": "Employee"
    #     })
    #     adrian = create(payload)

    #     payload = mk({
    #         "title": "Simutool Project",
    #         "type": mk_typ("project"),
    #         "member": [id(adrian), id(nasr)],
    #         "description": "Research Project"
    #     })
    #     st = create(payload)

    #     payload = mk({
    #         "identifier": id(st)})

    #     result = abox_service.get(payload)

    #     result_exp = mk(
    #         {"title": "Simutool Project",
    #         "type": [mk_typ("project")],
    #         "member": [id(nasr), id(adrian)],
    #         "identifier": id(st),
    #         "description": "Research Project"
    #         })

    #     assert result == result_exp

    # def test_get_project(self):
    #     payload = mk(
    #         {"identifier": "http://example.org/tbox/project"}
    #     )
    #     result = abox_service.get(payload)
    #     result_exp = mk(
    #         {"subclass_of": [mk_typ("activity")],
    #         "identifier": mk_typ("project"),
    #         "description": "An undertaking requiring concerted effort by Agents",
    #         "version": "3.2",
    #         "tags": ["TBox"],
    #         "title": "Project"})
    #     assert result == result_exp

#     def test_create_daniela_check_labels(self):
#         payload = mk({
#             "title": "Prof DN",
#             "type": mk_typ("user"),
#             "description": "Professor"
#         })
#         daniela = create(payload)
#         payload = mk(
#             {"identifier": id(daniela)}
#         )
#         result = abox_service.get(payload)
#         result_exp = mk({
#             "identifier": id(daniela),
#             "type": [mk_typ("user")],
#             "description": "Professor",
#             "tags": ["ABox", "user"],
#             "title": "Prof DN"
#             })
#         assert result == result_exp

#     def test_get_empty_id_should_fail(self):
#         payload = mk(
#             {"identifier": ""}
#         )
#         result = abox_service.get(payload)
#         result_exp = mk()
#         assert result == result_exp

        abox_service._clear_all()


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

    # def test_update_multiple_one_fails(self):
    #     payload = mk(
    #         {"title": "Prof DN",
    #         "type": mk_typ("user"),
    #         "description": "Professor"},
    #         {"title": "Mr AL",
    #         "type": mk_typ("user"),
    #         "description": "Employee"},
    #         {"title": "Mr NK",
    #         "type": mk_typ("user"),
    #         "description": "Employee"},
    #     )
    #     nodes = create(payload)
    #     payload = mk(
    #         {"identifier": id(nodes),
    #         "description": "Professor1"},
    #         {
    #         "description": "Employee1"},
    #         {"identifier": nodes["payload"][2]["identifier"],
    #         "description": "Employee2"},
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk(
    #         {"identifier": id(nodes),
    #         "type": [mk_typ("user")],
    #         "description": "Professor1",
    #         "tags": ["ABox", "user"],
    #         "title": "Prof DN"},
    #         {"identifier": nodes["payload"][2]["identifier"],
    #         "type": [mk_typ("user")],
    #         "description": "Employee2",
    #         "tags": ["ABox", "user"],
    #         "title": "Mr NK"}
    #     )
    #     assert result == result_exp
    #
    # def test_labels(self):
    #     payload = mk({
    #         "title": "Mr NK",
    #         "givenname": "N.",
    #         "type": mk_typ("user"),
    #         "description": "Employee"
    #     })
    #     nasr = create(payload)
    #     identifier = id(nasr)
    #     node = abox_service._node_matcher(identifier)
    #     node = node.first()
    #     node.add_label("label")
    #
    # def test_update_valid_rel(self):
    #     payload = mk(
    #         {"title": "Future IOT",
    #         "type": mk_typ("project"),
    #         "description": "Research Project"},
    #         {"title": "Simutool Project",
    #         "type": mk_typ("project"),
    #         "description": "Research Project"}
    #         )
    #     projects = create(payload)
    #     payload = mk(
    #         {"identifier": id(projects),
    #         "related": id(projects)}
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk(
    #     {"tags": ["ABox", "project"],
    #     "description": "Research Project",
    #     "title": "Future IOT",
    #     "identifier": id(result),
    #     "type": [mk_typ("project")],
    #     "related": [id(projects)]})
    #     assert result == result_exp
    #
    # def test_update_tags(self):
    #     payload = mk(
    #         {"title": "Future IOT",
    #         "type": mk_typ("project"),
    #         "description": "Research Project"})
    #     project = create(payload)
    #     payload = mk(
    #         {"identifier": id(project),
    #         "tags": "Testing"}
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk(
    #     {"tags": ["ABox", "project", "testing"],
    #     "description": "Research Project",
    #     "title": "Future IOT",
    #     "identifier": id(result),
    #     "type": [mk_typ("project")]})
    #     assert result == result_exp
    #
    # def test_update_invalid_attr_should_fail(self):
    #     payload = mk(
    #         {"title": "Future IOT",
    #         "type": mk_typ("project"),
    #         "description": "Research Project"})
    #     project = create(payload)
    #     payload = mk(
    #         {"identifier": id(project),
    #         "fake": "Testing"}
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk(
    #     {"tags": ["ABox", "project"],
    #     "description": "Research Project",
    #     "title": "Future IOT",
    #     "identifier": id(result),
    #     "type": [mk_typ("project")]})
    #     assert result == result_exp
    #
    # def test_update_empty_id_should_fail(self):
    #     payload = mk(
    #         {"identifier": "",
    #         "description": "Testing"}
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk()
    #     assert result == result_exp
    #
    # def test_update_empty_req_prop_should_fail(self):
    #     payload = mk(
    #         {"title": "Future IOT",
    #         "type": mk_typ("project"),
    #         "description": "Research Project"})
    #     project = create(payload)
    #     payload = mk(
    #         {"identifier": id(project),
    #         "description": ""}
    #     )
    #     result = abox_service.update(payload)
    #     result_exp = mk()
    #     assert result == result_exp

        abox_service._clear_all()


# class TestQuery:

#     def test_count_query(self):
#         query = "MATCH (n{identifier: "http://example.org/tbox/project"})RETURN count(n)"
#         result = abox_service.query(query)
#         result_exp = mk({"count(n)": 1})
#         assert result == result_exp

#     def test_query(self):
#         query = "MATCH (n{identifier: "http://example.org/tbox/project"})RETURN n.identifier"
#         result = abox_service.query(query)
#         result_exp = mk({"n.identifier": mk_typ("project")})
#         assert result == result_exp

#     def test_query_should_fail(self):
#         query = "MATCH (n) RETURN m"
#         result = abox_service.query(query)
#         result_exp = None
#         assert result == result_exp

#     def test_query_no_results_should_fail(self):
#         query = "MATCH (n:FBox) RETURN n"
#         result = abox_service.query(query)
#         result_exp = None
#         assert result == result_exp

#     def test_query_empty_should_fail(self):
#         query = ""
#         result = abox_service.query(query)
#         result_exp = None
#         assert result == result_exp

#     def test_query_blacklisted_should_fail(self):
#         query = "MATCH (n) DETACH DELETE n"
#         result = abox_service.query(query)
#         result_exp = None
#         assert result == result_exp

#         abox_service._clear_all()


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

    def test_delete_empty_should_fail(self):
        payload = mk()
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

    def test_delete_empty_id_should_fail(self):
        payload = mk({})
        result = abox_service.delete(payload)
        result_exp = [False]
        assert result == result_exp

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
#     def test_delete_empty_pl_should_fail(self):
#         payload = {}
#         result = abox_service.delete(payload)
#         result_exp = None
#         assert result == result_exp

#     def test_delete_missing_pl_should_fail(self):
#         payload = {"identifier":"fake"}
#         result = abox_service.delete(payload)
#         result_exp = None
#         assert result == result_exp

#     def test_delete_tbox_should_fail(self):
#         payload = mk({
#             "identifier": mk_typ("project")
#         })
#         result = abox_service.delete(payload)
#         result_exp = None
#         assert result == result_exp

        abox_service._clear_all()

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


    def test_is_instance_should_fail(self):
        pl = mk_typ("user")
        result = abox_service._is_instance(pl)
        result_exp = False
        assert result == result_exp

    def test_is_instance_should_fail2(self):
        pl = mk_typ("user2")
        result = abox_service._is_instance(pl)
        result_exp = False
        assert result == result_exp

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

    def test_is_class_should_fail(self):
        pl = mk_typ("user")
        result = abox_service._is_class(pl)
        result_exp = True
        assert result == result_exp

    def test_is_class_should_fail2(self):
        pl = mk_typ("user2")
        result = abox_service._is_class(pl)
        result_exp = False
        assert result == result_exp

    def test_get_subscribed_users(self):
        result = abox_service.get_subscribed_users()
        result_exp = 2
        assert len(result) == result_exp

    def test_post_notification_event(self):
        payload = mk({
            "title": "Mr NK",
            "givenname": "N.",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "n.k@uni-bamberg.de",
            "subscriber": True
        })
        self.nasr = create(payload)
        payload = mk({
            "title": "Mr AL",
            "givenname": "Adrian",
            "type": mk_typ("user"),
            "description": "Employee",
            "mbox": "a.l@uni-bamberg.de",
            "subscriber": True
        })
        actor = id(self.nasr)
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

    def test_get_tbox_node_by_title(self):
        class_title = "user"
        prop_name = None
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp = mk({
            'html_info': '',
            'description': 'People that create knowledge and have an account',
            'title': 'User',
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

    def test_get_tbox_node_by_title_prop(self):
        class_title = "user"
        prop_name = 'description'
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp = mk({
            'description': 'People that create knowledge and have an account',
        })
        assert result == result_exp

    def test_get_tbox_node_by_title_prop_invalid_class(self):
        class_title = "user2"
        prop_name = 'description'
        result = tbox_service._get_tbox_node_by_title(class_title, prop_name)
        result_exp = {'payload':[]}
        assert result == result_exp

        abox_service._clear_all()
