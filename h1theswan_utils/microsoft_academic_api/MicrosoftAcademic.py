from .config import MAGConf
import requests
from six import string_types

class MAGQueryType(object):
    HISTOGRAM = 0
    INTERPRET = 1
    EVALUATE = 2
    SIMILARITY = 3
    GRAPH_TRAVERSAL = 4
    UNKNOWN = 999

class QueryTypeError(ValueError):
    """
    The query type is not valid or not implemented.
    """


class MAGQuery(object):

    """Microsoft Academic API Query"""

    def __init__(self, query_type, arguments={}):
        """TODO: to be defined1. """
        self.query_type = query_type
        self.arguments = arguments

        self.url = MAGConf.BASE_URL  # will need to modify this later depending on the query type
        self.headers = {
            'Ocp-Apim-Subscription-Key': MAGConf.MICROSOFT_ACADEMIC_KEY
        }
        self.body = {}

        if isinstance(self.query_type, string_types):
            self.query_type = assign_query_type(self.query_type)

        if not isinstance(self.query_type, MAGQueryType) or self.query_type == MAGQueryType.UNKNOWN:
            raise QueryTypeError("invalid query type: {}".format(self.query_type))

        configure_query(self.query_type)

    def assign_query_type(qt):
        qt = qt.lower()
        if qt in ['histogram', 'hist', 'h']:
            return MAGQueryType.HISTOGRAM
        elif qt in ['interpret', 'interp', 'i']:
            return MAGQueryType.INTERPRET
        elif qt in ['evaluate', 'eval', 'e']:
            return MAGQueryType.EVALUATE
        elif qt in ['similarity', 'simil', 'sim', 's']:
            return MAGQueryType.SIMILARITY
        elif qt in ['graph_traversal', 'graph', 'gt', 'g']:
            return MAGQueryType.GRAPH_TRAVERSAL
        return MAGQueryType.UNKNOWN

    def configure_query(self, qtype):
        if qtype == MAGQueryType.HISTOGRAM:
            raise NotImplementedError("This query type is not yet implemented: {}".format(qtype))
        elif qtype == MAGQueryType.INTERPRET:
            pass
        elif qtype == MAGQueryType.EVALUATE:
            pass
        elif qtype == MAGQueryType.SIMILARITY:
            raise NotImplementedError("This query type is not yet implemented: {}".format(qtype))
        if qtype == MAGQueryType.GRAPH_TRAVERSAL:
            raise NotImplementedError("This query type is not yet implemented: {}".format(qtype))

class EvaluateQuery(object):

    """Docstring for EvaluateQuery. """

    def __init__(self):
        """TODO: to be defined1. """
        

        
