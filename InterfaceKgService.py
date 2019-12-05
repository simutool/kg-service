# This file contains all the functions that interface with the TBox
# It is the only middle-man between TBox and front-end.
import logging
from cachetools import cached, TTLCache
import KgService
cache = TTLCache(maxsize=10, ttl=30)

class InterfaceKgService(object):

    def __init__(self, graph_url, usr, pswd, path):
        self.initialize_logger()
        self.kgs = KgService(graph_url, usr, pswd, path)



    def initialize_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s' +
                            ' %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename='logfile.log')


    def create(self, payload, class_type):
        """
        This function is the front-facing interface to the Create function in the KgService

        Parameters
        ----------
        payload : dict
            dict that represents a json object.
            It must be of the form {'payload': [ instance1, instance2, ... ]},
            where each instance is of the form: { 'key1': 'val1', ...} 
            Example with one instance ("http://example.org/user"):
            {'payload': [{
                "title": "Mr NK",
                "mbox": "n.k@uni-bamberg.de",
                "type": "http://example.org/user",
                "description": "Employee"
            }]}

        class_type : string
            A URI of the class that the input is an instance of. See the excel sheet for info on URIs.
            Ex: "http://example.org/user" 
        Returns
        -------
        nothing

        """
        # payload = json.dumps(payload, default=kbms_converter)

        # class_type = TBOXI.get_model(class_name, 'identifier')

        if 'payload' in payload.keys():
            payload['payload'][0]['type'] = class_type
        else:
            payload['type'] = class_type
            payload = {'payload': [payload]}

        response = self.kgs.create(payload)

        return response


    def get(self, payload):
        res = self.kgs.get(payload)
        if len(res['payload']) != 0:
            return res
        return None


    # return True if there is an instance in the DB with this uri.
    # must return false if a class has this uri
    def is_instance(uri):
        # To be implemented
        pass


    @cached(cache)
    def get_instances(self, class_type):
        result = self.kgs.get_instances(class_type)
        
        if not isinstance(result, Exception):
            result = result['payload']
        return result


    def query(self, graph_query):
        # To be implemented
        pass


    def get_id_by_email(self, email):
        q = 'MATCH (n {mbox:"%s"}) RETURN n.identifier' % email
        res = self.kgs.query(q)['payload']
        try:
            res = res[0]['n.identifier']
        except Exception as e:
            return None
        return res


    def update(self, payload):
        if 'payload' not in payload.keys():
            payload = {'payload': [payload]}

        response = self.kgs.update(payload)

        return response


    def delete(self, payload):
        if 'payload' not in payload.keys():
            payload = {'payload': [payload]}

        response = self.kgs.delete(payload)
        return response
