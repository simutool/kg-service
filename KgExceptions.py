class KgExceptions(object):
    def __init__(self):
        pass

    def _exception_path(self):
        msg = ('<Subject,Predicate,Object> definition not satisfied. ' +
               'Check the semantics of input against the domain model.')
        return KeyError(msg)

    def _exception_empty(self):
        msg = ('Payload is empty.')
        return ValueError(msg)

    def _exception_type_empty(self, d):
        msg = ('"type" is required. Your input: %s. ' % d +
               'This instance will not be created.')
        return ValueError(msg)

    def _exception_req_prop(self, prop, d):
        msg = ('Required property is not provided or empty: "%s". ' % (prop) +
               'Your input: %s' % (d))
        return ValueError(msg)

    def _exception_blacklisted(self, query):
        msg = ('No modifying functions allowed. Your query: "%s" ' % (query))
        return ValueError(msg)

    def _exception_non_existant(self, ident):
        msg = ('This identifier is not existant or empty. Your input: %s' % ident)
        return KeyError(msg)

    def _exception_no_instance(self, obj):
        msg = ('This object has no instances: %s' % obj)
        return KeyError(msg)

    def _exception_delete(self, obj):
        msg = ('This object cannot be deleted: %s' % obj)
        return KeyError(msg)

    def _exception_cypher(self, query):
        msg = ('No results for this query: %s' % query)
        return ValueError(msg)

    def _exception_not_tbox(self, obj):
        msg = ('This object is not a TBox element: %s' % obj)
        return KeyError(msg)
