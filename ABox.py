from abc import ABCMeta, abstractmethod
from KgService import *

logger = logging.getLogger('web2py.app.simutool_kms.kgservice')

class ABoxService (KgService):

    def __init__(self, url, user, pwd, path=''):
        super(ABoxService, self).__init__(url, user, pwd, model='ABox', meta='TBox', path=path)


    def get_model_label(self):
        return "ABox"

	# def get_self_descendants(self, payload):
	# 	return self._get_self_descendants(payload, "subclass_of")

KgService.register(ABoxService)

#a=ABoxService("http://141.13.162.157:7774/db/data/","neo4j", "kgservice.testing", model='ABox', meta='TBox')
