import unittest
from py2neo import *
from KgService import *
#import dm_service
from ABox import *

class TestStringMethods(unittest.TestCase):
    print(" ### Testing Environment ### ")
    print("Initializing graph connection...")
    kgservice = ABoxService("http://141.13.162.157:7774/db/data/","neo4j", "kgservice.testing")

    kgservice._clear_all()

    tbox_base_identifier = 'http://example.org/tbox/'
    print("# ---- Creating classes...")
    q = """
    MERGE
    (a:TBox{identifier:"http://example.org/tbox/agent"})
    CREATE
    (c:TBox{title:"University", identifier:"http://example.org/tbox/university"})-[:subclass_of]->(a)

    CREATE
    (p:TBox{title:"University of Applied Sciences", identifier:"http://example.org/tbox/university-as"})-[:subclass_of]->(c)

    CREATE
    (s:TBox{title:"Full University", identifier:"http://example.org/tbox/university-full"})-[:subclass_of]->(c)

    CREATE
    (t:TBox{title:"Technical University", identifier:"http://example.org/tbox/university-tech"})-[:subclass_of]->(s)
    """
    result = kgservice.graph.run(q)
    print("ok")
    def create(payload):
        return kgservice.create(payload)
    print("# ---- Creating instances...")
    global org_bamberg
    global stephane_bechtel
    global agi_demo_600
    global cad_agid6m
    global pre_preg_cf_175
    global ppcf_175_spec
    global rtm6_resin
    global twi
    global jasmin_stein
    global ppcf
    global loiretech_sas
    global remi_chauveau
    global tools_agi_dem
    global ecole_centrale_de_nantes
    global hermine_tertrais
    global ecn_simulation_for_agi_demonstrator
    global uni_hof
    global uni_cob
    global uni_bbg
    global uni_bay
    global thing
    # below should all be created:
    payload  = {'payload':[{
        'title': 'Thing',
        'type': tbox_base_identifier + 'kbmsthing',
        'description': 'a thing to do test cases with',
    }]}
    thing = kgservice.create(payload)

    payload  = {'payload':[{
        'title': 'University of Bamberg',
        'type': tbox_base_identifier + 'organization',
        # 'related': tbox_base_identifier + 'productdesign',
    }]}
    org_bamberg = kgservice.create(payload)
    print org_bamberg

    payload = {'payload':[{
        'title': 'Stephane Bechtel',
        'familyName': 'Bechtel',
        'givenName': 'Stephane',
        'type': tbox_base_identifier + 'user',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    stephane_bechtel = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'AGI Demonstrator 600mm',
        'type': tbox_base_identifier + 'part',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    agi_demo_600 = kgservice.create(payload)
#    print agi_demo_600

    payload = {'payload':[{
        'title': 'CAD AGID6m',
        'type': tbox_base_identifier + 'document',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    cad_agid6m = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Pre-Preg CF_175',
        'type': tbox_base_identifier + 'material',
        'related': agi_demo_600['payload'][0]['identifier'],
    }]}
    pre_preg_cf_175 = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'PPCF_175 spec',
        'type': tbox_base_identifier + 'document',
        'related': pre_preg_cf_175['payload'][0]['identifier'],
    }]}
    ppcf_175_spec = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'RTM6_resin',
        'type': tbox_base_identifier + 'material',
        'related': agi_demo_600['payload'][0]['identifier'],
    }]}
    rtm6_resin = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'TWI',
        'type': tbox_base_identifier + 'organization',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    twi = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Jasmin Stein',
        'givenName': 'Jasmin',
        'familiyName': 'Stein',
        'type': tbox_base_identifier + 'user',
        'related': twi['payload'][0]['identifier'],
    }]}
    jasmin_stein = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'PPCF_175_Msrmt',
        'type': tbox_base_identifier + 'document',
        'related': [org_bamberg['payload'][0]['identifier'], pre_preg_cf_175['payload'][0]['identifier']],
    }]}
    ppcf = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Loiretech SAS',
        'type': tbox_base_identifier + 'organization',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    loiretech_sas = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Remi Chauveau',
        'givenName': 'Remi',
        'familiyName': 'Chauveau',
        'type': tbox_base_identifier + 'user',
        'related': loiretech_sas['payload'][0]['identifier'],
    }]}
    remi_chauveau = kgservice.create(payload)

    payload = {'payload':[
        {
            'title': 'Tool AGI Dem 1',
            'type': tbox_base_identifier + 'tool',
            'related': org_bamberg['payload'][0]['identifier'],
        },
        {
            'title': 'Tool AGI Dem 2',
            'type': tbox_base_identifier + 'tool',
            'related': org_bamberg['payload'][0]['identifier'],
        }
    ]}
    tools_agi_dem = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Ecole Centrale de Nantes',
        'type': tbox_base_identifier + 'organization',
        'related': org_bamberg['payload'][0]['identifier'],
    }]}
    ecole_centrale_de_nantes = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Hermine Tertrais',
        'givenName': 'Hermine',
        'familiyName': 'Tertrais',
        'type': tbox_base_identifier + 'user',
        'related': ecole_centrale_de_nantes['payload'][0]['identifier'],
    }]}
    hermine_tertrais = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'ECN Simulation for AGI demonstrator',
        'type': tbox_base_identifier + 'simulator',
        'related': org_bamberg['payload'][0]['identifier'],
        },
    ]}
    ecn_simulation_for_agi_demonstrator = kgservice.create(payload)

    payload = {'payload':[{
        'title': 'Hof University',
        'type': tbox_base_identifier + 'university-as'
        }
    ]}
    uni_hof = kgservice.create(payload)
    payload = {'payload':[{
        'title': 'Coburg University',
        'type': tbox_base_identifier + 'university-as'
        }
    ]}
    uni_cob = kgservice.create(payload)
    payload = {'payload':[{
        'title': 'Bamberg University',
        'type': tbox_base_identifier + 'university-full'
        }
    ]}
    uni_bbg = kgservice.create(payload)
    payload = {'payload':[{
        'title': 'Bayreuth University',
        'type': tbox_base_identifier + 'university-full'
        }
    ]}
    uni_bay = kgservice.create(payload)

    print("ok")
    def test_01_create(self):
        print("# ---- Testing create function...")
        #case single instance:
        global nasr_kasrin
        payload = {'payload':[{
            'title': 'Nasr Kasrin',
            'givenName': 'Nasr',
            'type': self.tbox_base_identifier + 'user'
        }]}
        nasr_kasrin = self.kgservice.create(payload)
        print  nasr_kasrin
        result_exp = {'payload':[{
            'title': 'Nasr Kasrin',
            'givenName': 'Nasr',
            'identifier': nasr_kasrin['payload'][0]['identifier'],
            'type': ['http://example.org/tbox/user']
        }]}
        self.assertEqual(nasr_kasrin, result_exp)
        #case multiple instances
        global mobi
        payload = {'payload':[
            {
                'type': self.tbox_base_identifier + 'user',
                'title': 'Adrian Lengenfelder',
                'givenName':'Adrian',
                'familyName': 'Lengenfelder',
                'related': org_bamberg['payload'][0]['identifier']
            },
            {
                'type': self.tbox_base_identifier + 'oven',
                'title': 'Maliha Qureshi',
                'givenName':'Maliha',
                'familyName': 'Qureshi',
                'related': org_bamberg['payload'][0]['identifier']
            }
        ]}
        mobi = self.kgservice.create(payload)
        result_exp = {'payload':[
            {
                'type': ['http://example.org/tbox/user'],
                'title': 'Adrian Lengenfelder',
                'givenName':'Adrian',
                'familyName': 'Lengenfelder',
                'related': [org_bamberg['payload'][0]['identifier']],
                'identifier': mobi['payload'][0]['identifier']
            },
            {
                'type': ['http://example.org/tbox/oven'],
                'title': 'Maliha Qureshi',
                'givenName':'Maliha',
                'familyName': 'Qureshi',
                'related': [org_bamberg['payload'][0]['identifier']],
                'identifier': mobi['payload'][1]['identifier']
            }
        ]}
        self.assertEqual(mobi, result_exp)
        #case relation to other node
        global lukas_genssler
        payload = {'payload':[{
            'title': 'Lukas Genssler',
            'givenName': 'Lukas',
            'type': self.tbox_base_identifier + 'user',
            'related': mobi['payload'][1]['identifier']
        }]}
        lukas_genssler = self.kgservice.create(payload)
        result_exp = {'payload':[{
            'title': 'Lukas Genssler',
            'givenName': 'Lukas',
            'identifier': lukas_genssler['payload'][0]['identifier'],
            'type': ['http://example.org/tbox/user'],
            'related': [mobi['payload'][1]['identifier']]
        }]}
        self.assertEqual(lukas_genssler, result_exp)
        #case no relations
        global daniela_nicklas
        payload = {'payload':[{
            'type': self.tbox_base_identifier + 'user',
            'title': 'Daniela Nicklas'
        }]}
        daniela_nicklas = self.kgservice.create(payload)
        result_exp = {'payload':[{
            'type': ['http://example.org/tbox/user'],
            'identifier': daniela_nicklas['payload'][0]['identifier'],
            'title': 'Daniela Nicklas'
        }]}
        self.assertEqual(daniela_nicklas, result_exp)
        #case no properties at all
        global unknown
        payload = {'payload':[{
            'type': self.tbox_base_identifier + 'user'
        }]}
        unknown = self.kgservice.create(payload)
        result_exp = {'payload':[{
            'type': ['http://example.org/tbox/user'],
            'identifier': unknown['payload'][0]['identifier'
        ]}]}
        self.assertEqual(unknown, result_exp)
        #case create mult. rels of same type
        global francois
        payload = {'payload':[{
            'type': self.tbox_base_identifier + 'user',
            'title': 'Francois Francais',
            'givenName':'Francois',
            'related':[mobi['payload'][0]['identifier'], mobi['payload'][1]['identifier']]
        }]}
        francois = self.kgservice.create(payload)
        result_exp = {'payload':[{
            'type': ['http://example.org/tbox/user'],
            'related': [mobi['payload'][1]['identifier'], mobi['payload'][0]['identifier']],
            'identifier': francois['payload'][0]['identifier'],
            'givenName': 'Francois',
            'title': 'Francois Francais'}]}
        self.assertEqual(francois, result_exp)

        #case entity path not valid
        payload = {'payload':[{
            'type': self.tbox_base_identifier + 'user',
            'title': 'Monsieur Incognito',
            'givenName1':'Monsieur',
            'member':[mobi['payload'][0]['identifier'], mobi['payload'][1]['identifier']]
        }]}
        result = self.kgservice.create(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case not all required properties
        payload = {'payload':[{
            'type': self.tbox_base_identifier + 'kbmsthing'
        }]}
        kbms = self.kgservice.create(payload)
        result_exp = ValueError()

        self.assertEqual(type(kbms), type(result_exp))
        ## Nodes below should NOT be created ##
        #case: type is not existant, should not create node
        payload = {'payload':[{
            'type': 'http://example.org/tbox/user_false',
            'title': 'Valentyna'}]}
        result = self.kgservice.create(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        # case: empty type
        payload = {'payload':[{
            'type': '',
            'title': 'Valentyna'
        }]}
        result = self.kgservice.create(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case1: empty payload
        payload = {}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case2: empty payload
        payload = []
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case3: empty payload
        payload = {'payload':[]}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case4: empty payload
        payload = {'payload':[{}]}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case5: false payload
        payload = {False}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case6: false payload
        payload = [False]
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case:  list payload
        payload = ['e']
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case: char payload
        payload = 'e'
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case: wrong payload
        payload = '1%2'
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case: int payload
        payload = 1
        result = self.kgservice.create(payload)
        result_exp = TypeError()
        self.assertEqual(type(result), type(result_exp))
        # case: empty type
        payload = {'payload':[{'title': 'Valentyna'}]}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case not all required properties in payload
        payload = {'payload':[{'type': 'http://example.org/tbox/kbmsthing', 'title': 'monster'}]}
        result = self.kgservice.create(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))

        print("ok")
    def test_02_get_instances(self):
        print("# ---- Testing get_instances function")
        #case returning the instances of university
        identifier = {'payload': [{'identifier': 'http://example.org/tbox/university'}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = {'payload':[
            {
                'title': uni_hof['payload'][0]['title'],
                'identifier': uni_hof['payload'][0]['identifier'],
            },
            {
                'title': uni_cob['payload'][0]['title'],
                'identifier': uni_cob['payload'][0]['identifier'],
            },
            {
                'title': uni_bbg['payload'][0]['title'],
                'identifier': uni_bbg['payload'][0]['identifier'],
            },
            {
                'title': uni_bay['payload'][0]['title'],
                'identifier': uni_bay['payload'][0]['identifier'],
            }
        ]}
        self.assertItemsEqual(result, result_exp)
        #case returning the instances of engineering
        identifier = {'payload': [{'identifier': 'http://example.org/tbox/resource'}]}
        result = self.kgservice.get_instances(identifier)
        result = len(result['payload'])
        result_exp = 6
        self.assertEqual(result, result_exp)
        #case class identifier is not existing
        identifier = {'payload': [{'identifier': 'http://example.org/abox/agi'}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case class identifier is not existant
        identifier = {'payload': [{'identifier': 'http://example.org/abox/agiFalse'}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case type is empty
        identifier = ''
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case class identifier is space
        identifier = ' '
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case class identifier is False(bool)
        identifier = False
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case class identifier is None
        identifier = None
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        identifier = {}
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        identifier = []
        result = self.kgservice.get_instances(identifier)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case: char identifier
        identifier = {'payload': [{'identifier': 'e'}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case: char payload
        identifier = {'payload': [{'identifier': '1%2'}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))

        #case:  identifier in list
        identifier = {'payload': [{'identifier': ['e']}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        #case: int identifier
        identifier = {'payload': [{'identifier': 1}]}
        result = self.kgservice.get_instances(identifier)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))

        print("ok")
    def test_03_get(self):
        print("# ---- Testing get function...")
        # case existant identifier: return relations and properties
        identifier = mobi['payload'][0]['identifier']
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = {'payload':[{
            'type': [self.tbox_base_identifier + 'user'],
            'title': 'Adrian Lengenfelder',
            'givenName':'Adrian',
            'familyName': 'Lengenfelder',
            'related': [org_bamberg['payload'][0]['identifier']],
            'identifier': mobi['payload'][0]['identifier']
        }]}
        self.assertEqual(result, result_exp)
        #case non existant identifier
        identifier = 'http://example.org/abox/adrian1'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        payload = ''
        result = self.kgservice.get(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case false identifier
        payload = False
        result = self.kgservice.get(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        identifier = '1'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case: char identifier
        identifier = 'e'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case: char payload
        identifier = '1%2'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))

        #case:  identifier in list
        identifier = ['e']
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        #case: int identifier
        identifier = 1
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get(payload)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        print("ok")
    def test_04_get_self_descendants(self):
        print("# ---- Testing get self descendants function...")
        # case
        identifier = "http://example.org/tbox/university"
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get_self_descendants(payload)
        result_exp = {'payload':[{
            'subclass_of': ['http://example.org/tbox/university-full',
                            'http://example.org/tbox/university-as',
                            'http://example.org/tbox/university-tech'],
            'identifier': 'http://example.org/tbox/university',
            'title': 'University'}]}
        self.assertItemsEqual(result['payload'][0]['subclass_of'], result_exp['payload'][0]['subclass_of'])

        print("ok")
    def test_05__identifier_generator(self):
        print("# ---- Testing _identifier_generator function...")
        identifier = self.kgservice._identifier_generator()
        self.assertIsNotNone(identifier)

        print("ok")
    # def test_06__is_relation(self):
    #     print("# ---- Testing _is_relation function...")
    #     #case relation as property
    #     payload = 'uploader'
    #     result = dm_service._is_relation(payload)
    #     result_exp = True
    #     self.assertEqual(result, result_exp)
    #     #case relation as property
    #     payload = 'Uploader'
    #     result = dm_service._is_relation(payload)
    #     result_exp = True
    #     self.assertEqual(result, result_exp)
    #     #case attribute as property
    #     payload = 'name'
    #     result = dm_service._is_relation(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     #case poperty is empty
    #     payload = ''
    #     result = dm_service._is_relation(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     #case relation as property
    #     payload = 'uploader2'
    #     result = dm_service._is_relation(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     #case relation as property
    #     payload = 1
    #     result = dm_service._is_relation(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     #case list
    #     payload = ['uploader2']
    #     result = dm_service._is_relation(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     print("ok")
    # def test_06__is_property(self):
    #     print("# ---- Testing _is_property function...")
    #     #case true
    #     payload = 'title'
    #     result = dm_service._is_property(payload)
    #     result_exp = True
    #     self.assertEqual(result, result_exp)
    #     #case false
    #     payload = 'name'
    #     result = dm_service._is_property(payload)
    #     result_exp = False
    #     self.assertEqual(result, result_exp)
    #     print("ok")
    def test_07_update(self):
        print("# ---- Testing update function...")
        # case updating relations
        payload = {'payload':[{
            'identifier': mobi['payload'][0]['identifier'],
            'givenName':'Adrian',
            'related': [org_bamberg['payload'][0]['identifier']]
            # 'related': 'http://example.org/tbox/agent'
        }]}
        result = self.kgservice.update(payload)
        result_exp = {'payload':[{
            'type': [self.tbox_base_identifier + 'user'],
            'title': 'Adrian Lengenfelder',
            'givenName':'Adrian',
            'familyName': 'Lengenfelder',
            'related': [org_bamberg['payload'][0]['identifier']],
            'identifier': mobi['payload'][0]['identifier']
        }]}
        self.assertItemsEqual(result['payload'][0]['related'], result_exp['payload'][0]['related'])
        # case updating properties
        payload = {'payload':[{
            'identifier': mobi['payload'][0]['identifier'],
            'givenName': 'Addi'
        }]}
        result = self.kgservice.update(payload)
        result_exp = {'payload':[{
            'type': [self.tbox_base_identifier + 'user'],
            'title': 'Adrian Lengenfelder',
            'givenName':'Addi',
            'familyName': 'Lengenfelder',
            'related': [org_bamberg['payload'][0]['identifier']],
            'identifier': mobi['payload'][0]['identifier']
        }]}
        self.assertItemsEqual(result['payload'][0]['givenName'], result_exp['payload'][0]['givenName'])

        # case non valid path
        payload = {'payload':[{
            'identifier': mobi['payload'][0]['identifier'],
            'contributor': [org_bamberg['payload'][0]['identifier']]
        }]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))

        # case required properties not fulfilled
        payload = {'payload':[{
            'identifier': thing['payload'][0]['identifier'],
            'description': ''
        }]}
        result = self.kgservice.update(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))

        #case empty identifier
        payload = {'payload':[{
            'identifier': '',
            'phone':'98765',
            'uploader':['http://example.org/abox/agi']
        }]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case identifier not existant
        payload = {'payload':[{
            'identifier': 'http://example.org/abox/adrianlengenfelder',
            'name':'ADRIAN',
            'related':'http://example.org/abox/adrian'}]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case identifier false
        payload = {'payload':[{'identifier': False }]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case identifier empty list
        payload = {'payload':[{'identifier': [] }]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case no identifier
        payload = {'payload':[{'phone':'98765'}]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
         #case no identifier
        payload = {'payload':[{'phone':'98765'}]}
        result = self.kgservice.update(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))

        print("ok")
    def test_08_query(self):
        print("# ---- Testing query funtion...")
        # case normal query
        query = "MATCH (n {title: 'Adrian Lengenfelder'}) RETURN count(n)"
        result = self.kgservice.query(query)
        result_exp = {'payload': [{'count(n)': 1}]}
        self.assertEqual(result, result_exp)
        # case empty query
        query = ""
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case modifying function
        query = "MATCH (n) DETACH DELETE n"
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case wrong query
        query = "MATCH (n) RETURN m"
        result = self.kgservice.query(query)
        result_exp = (u'SyntaxError: Variable `m` not defined (line 1, column 18 (offset: 17))\n"MATCH (n) RETURN m"\n                  ^',)
        self.assertEqual(result.args, result_exp)

        # case query false
        query = False
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case query false
        query = 1
        result = self.kgservice.query(query)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        # case query false
        query = []
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case query false
        query = {}
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        # case query empty string
        query = ""
        result = self.kgservice.query(query)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        print("ok")
    def test_08_bug_fixing(self):
        print("# ---- Testing bug fixing")
        q = """MATCH (n {identifier: 'http://example.org/tbox/tool'})<-[r:subclass_of]-(m)
        CREATE (n)<-[r2:subclass_of]-(m)
        SET r2 = r
        WITH r
        DELETE r"""
        result = self.kgservice.graph.run(q)
        # get instance not finding all get_instances
        identifier = 'http://example.org/tbox/resource'
        result = self.kgservice.get_instances(identifier)
        #
        identifier = 'http://example.org/tbox/tool'
        result = self.kgservice.get_instances(identifier)

        print("ok")
    def test_08_internal(self):
        print("# ---- Testing internal functions")
        # format output
        payload = {'identifier': 1}
        result = self.kgservice._format_output(payload)
        result_exp = {'payload':[{'identifier': 1 }]}
        self.assertEqual(result, result_exp)

        # case
        identifier = "http://example.org/tbox/university"
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.get_self_descendants(payload)
        result_exp = {'payload':[{
            'subclass_of': ['http://example.org/tbox/university-full', 'http://example.org/tbox/university-as'],
            'identifier': 'http://example.org/tbox/university',
            'title': 'University'}]}
        # self.assertItemsEqual(result, result_exp)

        # # case get_relation_path
        relation = 'related'
        path = dm_service.get_relation_path(relation)
        type_from = self.tbox_base_identifier + path[0]
        relation = path[1]
        type_to = self.tbox_base_identifier + path[2]
        path_new = (type_from, relation, type_to)


        pl1 = nasr_kasrin['payload'][0]['identifier']
        pl2 = 'http://example.org/tbox/person'
        result = self.kgservice._is_decendant(pl1, pl2)
        result_exp = True
        self.assertEqual(result, result_exp)

        payload = nasr_kasrin['payload'][0]['identifier']
        result = self.kgservice._get_type(payload)
        # print("result: ", result)

        print("ok")
    def test_08__get_path(self):
        print("# ---- Testing get_path")
        # get self decendants
        identifier = "http://example.org/tbox/university"
        result = self.kgservice._get_path(identifier,rel="subclass_of", inv=True, degree=-1)
        result_exp = ['http://example.org/tbox/university-full',
                            'http://example.org/tbox/university-as',
                            'http://example.org/tbox/university-tech']
        self.assertItemsEqual(result, result_exp)
        # get_instances
        identifier = 'http://example.org/tbox/university'
        result = self.kgservice._get_path(identifier,rel="subclass_of", inv=True, degree=-1)
        result = self.kgservice._get_path(result,rel="type", inv=True, degree=-1)
        result_exp =[
                uni_hof['payload'][0]['identifier'],
                uni_cob['payload'][0]['identifier'],
                uni_bbg['payload'][0]['identifier'],
                uni_bay['payload'][0]['identifier'],
        ]
        self.assertItemsEqual(result, result_exp)
        # get self decendants BREAKS
        identifier = "http://example.org/tbox/university2"
        result = self.kgservice._get_path(identifier,rel="subclass_of", inv=True, degree=-1)
        result_exp = []
        self.assertItemsEqual(result, result_exp)
    def test_09_delete(self):
        print("# ---- Testing delete function...")
        nodes = [
            org_bamberg['payload'][0]['identifier'],
            stephane_bechtel['payload'][0]['identifier'],
            agi_demo_600['payload'][0]['identifier'],
            cad_agid6m['payload'][0]['identifier'],
            pre_preg_cf_175['payload'][0]['identifier'],
            ppcf_175_spec['payload'][0]['identifier'],
            rtm6_resin['payload'][0]['identifier'],
            twi['payload'][0]['identifier'],
            jasmin_stein['payload'][0]['identifier'],
            ppcf['payload'][0]['identifier'],
            loiretech_sas['payload'][0]['identifier'],
            remi_chauveau['payload'][0]['identifier'],
            tools_agi_dem['payload'][0]['identifier'],
            tools_agi_dem['payload'][1]['identifier'],
            ecole_centrale_de_nantes['payload'][0]['identifier'],
            hermine_tertrais['payload'][0]['identifier'],
            ecn_simulation_for_agi_demonstrator['payload'][0]['identifier'],
            uni_hof['payload'][0]['identifier'],
            uni_cob['payload'][0]['identifier'],
            uni_bbg['payload'][0]['identifier'],
            uni_bay['payload'][0]['identifier'],
            thing['payload'][0]['identifier'],

            nasr_kasrin['payload'][0]['identifier'],
            mobi['payload'][0]['identifier'],
            mobi['payload'][1]['identifier'],
            lukas_genssler['payload'][0]['identifier'],
            daniela_nicklas['payload'][0]['identifier'],
            unknown['payload'][0]['identifier'],
            francois['payload'][0]['identifier']
        ]
        for identifier in nodes:
            payload = {'payload': [{'identifier': identifier}]}
            result = self.kgservice.delete(payload)
            result_exp = [True]
            self.assertEqual(result, result_exp)
        q = "MATCH (c:TBox{identifier:'http://example.org/tbox/university'}) DETACH DELETE c"
        result = self.kgservice.graph.run(q)
        q = "MATCH (c:TBox{identifier:'http://example.org/tbox/university-as'}) DETACH DELETE c"
        result = self.kgservice.graph.run(q)
        q = "MATCH (c:TBox{identifier:'http://example.org/tbox/university-full'}) DETACH DELETE c"
        result = self.kgservice.graph.run(q)
        q = "MATCH (c:TBox{identifier:'http://example.org/tbox/university-tech'}) DETACH DELETE c"
        result = self.kgservice.graph.run(q)
        # Test cases:
        #case non existant node
        identifier = 'http://example.org/abox/adrianlengenfelder'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.delete(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case existant tbox identifier
        identifier = 'http://example.org/tbox/engineering'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.delete(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case no label assigned
        identifier = 'http://example.org/nolabel'
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.delete(payload)
        result_exp = KeyError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        payload = ''
        result = self.kgservice.delete(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        payload = []
        result = self.kgservice.delete(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))
        #case empty identifier
        payload = None
        result = self.kgservice.delete(payload)
        result_exp = ValueError()
        self.assertEqual(type(result), type(result_exp))

        #case list
        identifier = ['e']
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.delete(payload)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        #case int identifier
        identifier = 1
        payload = {'payload': [{'identifier': identifier}]}
        result = self.kgservice.delete(payload)
        result_exp = AttributeError()
        self.assertEqual(type(result), type(result_exp))
        print("ok")

if __name__ == '__main__':
    unittest.main()
