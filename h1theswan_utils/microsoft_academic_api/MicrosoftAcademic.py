from .config import MAGConf
import requests
from six import string_types, iteritems, itervalues

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

class QueryPostError(RuntimeError):
    """
    Error when issuing query POST
    """

class QueryGetError(RuntimeError):
    """
    Error when issuing query GET
    """

class QueryTimeoutError(RuntimeError):
    """
    Timeout Error when issuing query POST
    """


class MAGQuery(object):

    """Microsoft Academic API Query"""

    def __init__(self):
        """TODO: to be defined1. """
        self.query_type = MAGQueryType.UNKNOWN

        self.url = MAGConf.BASE_URL  # will need to modify this later depending on the query type
        self.body = {}
        self.headers = {}

        # if isinstance(self.query_type, string_types):
        #     self.query_type = assign_query_type(self.query_type)

        # if not isinstance(self.query_type, magquerytype) or self.query_type == magquerytype.unknown:
        #     raise QueryTypeError("invalid query type: {}".format(self.query_type))

    def get_headers(self):
        return {
            'Ocp-Apim-Subscription-Key': MAGConf.SUBSCRIPTION_KEY
        }

    def get_url(self):
        raise NotImplementedError("get_url() is not implemented in base class")

    def get_body(self):
        raise NotImplementedError("get_body() is not implemented in base class")

    def post(self, return_json=True):
        url = self.get_url()
        headers = self.get_headers()
        body = self.get_body()
        r = requests.post(url, data=body, headers=headers)
        if r.status_code >= 300:
            raise QueryPostError("An error occurred during the query. Status code: {}".format(r.status_code))
        j = r.json()
        if j.get('aborted'):
            raise QueryTimeoutError("The query POST request encountered a timeout and aborted")
        if return_json:
            return j
        else:
            return r

    def get(self, return_json=True):
        # for Evaluate and Interpret queries, get() can be used as an alternative to post()
        url = self.get_url()
        headers = self.get_headers()
        body = self.get_body()
        r = requests.get(url, params=body, headers=headers)
        if r.status_code >= 300:
            raise QueryGetError("An error occurred during the query. Status code: {}".format(r.status_code))
        j = r.json()
        if j.get('aborted'):
            raise QueryTimeoutError("The query GET request encountered a timeout and aborted")
        if return_json:
            return j
        else:
            return r


    # def assign_query_type(qt):
    #     qt = qt.lower()
    #     if qt in ['histogram', 'hist', 'h']:
    #         return MAGQueryType.HISTOGRAM
    #     elif qt in ['interpret', 'interp', 'i']:
    #         return MAGQueryType.INTERPRET
    #     elif qt in ['evaluate', 'eval', 'e']:
    #         return MAGQueryType.EVALUATE
    #     elif qt in ['similarity', 'simil', 'sim', 's']:
    #         return MAGQueryType.SIMILARITY
    #     elif qt in ['graph_traversal', 'graph', 'gt', 'g']:
    #         return MAGQueryType.GRAPH_TRAVERSAL
    #     return MAGQueryType.UNKNOWN


class EvaluateQuery(MAGQuery):

    """Docstring for EvaluateQuery. """

    URL = MAGConf.BASE_URL + '/evaluate'
    def __init__(self, expr=None,
                    attributes=None,
                    count=None,
                    offset=None,
                    model=None):
        """TODO: to be defined1. """
        MAGQuery.__init__(self)

        self.query_type = MAGQueryType.EVALUATE

        self.expr = expr
        self.attributes = attributes or MAGConf.EVALUATE_QUERY_DEFAULTS['attributes']
        self.count = count or MAGConf.EVALUATE_QUERY_DEFAULTS['count']
        self.offset = offset or MAGConf.EVALUATE_QUERY_DEFAULTS['offset']
        self.model = model or MAGConf.EVALUATE_QUERY_DEFAULTS['model']

    def get_url(self):
        return self.URL

    def get_body(self):
        if not self.expr:
            raise RuntimeError("the evaluate query needs an expr")

        args = {
            'expr': self.expr,
            'attributes': self.attributes,
            'count': self.count,
            'offset': self.offset,
            'model': self.model
        }
        return args
    
class InterpretQuery(MAGQuery):

    """Docstring for InterpretQuery. """

    URL = MAGConf.BASE_URL + '/interpret'
    def __init__(self, query=None,
            complete=None,
            count=None,
            offset=None,
            timeout=None,
            model=None):
        """

        :query: TODO
        :complete: TODO
        :count: TODO
        :offset: TODO
        :timeout: TODO
        :model: TODO

        """
        MAGQuery.__init__(self)

        self.query_type = MAGQueryType.INTERPRET

        self.query = query
        self.complete = complete or MAGConf.INTERPET_QUERY_DEFAULTS['complete']
        self.count = count or MAGConf.INTERPET_QUERY_DEFAULTS['count']
        self.offset = offset or MAGConf.INTERPET_QUERY_DEFAULTS['offset']
        self.timeout = timeout or MAGConf.INTERPET_QUERY_DEFAULTS['timeout']
        self.model = model or MAGConf.INTERPET_QUERY_DEFAULTS['model']

    def get_url(self):
        return self.URL

    def get_body(self):
        if not self.query:
            raise RuntimeError("the interpret query needs a query")

        args = {
            'query': self.query,
            'complete': self.complete,
            'count': self.count,
            'offset': self.offset,
            'timeout': self.timeout,
            'model': self.model
        }
        return args

    def get_first_expr(self, query=None):
        """Issue a GET request and get the first expression from the query
        :returns: expr (string), to use in an Evaluate query

        """
        if query:
            self.query = query
        # j = self.post()
        # POST method has been giving me trouble. use GET instead
        j = self.get()
        interpretations = j.get('interpretations')
        if not interpretations:
            return None
        rules = interpretations[0]['rules']
        first_result = rules[0]['output']
        if first_result['type'] != 'query':
            raise RuntimeError("unexpected---first result is not type: query (type: {})".format(first_result['type']))
        return first_result.get('value')
        

        
def get_first_result_from_query(query, attributes=None):
    expr = InterpretQuery().get_first_expr(query)
    if expr:
        q = EvaluateQuery(expr, count=1, attributes=attributes)
        # j = q.post()
        # POST method has been giving me trouble. use GET instead
        j = q.get()
        if j:
            return j['entities'][0]
    return None

def get_top_results_from_query(query, n=10, attributes=None):
    expr = InterpretQuery().get_first_expr(query)
    if expr:
        q = EvaluateQuery(expr, count=n, attributes=attributes)
        # j = q.post()
        # POST method has been giving me trouble. use GET instead
        j = q.get()
        if j:
            return j['entities']
    return None

def convert_inverted_abstract_to_abstract_words(inverted_abstract, index_length=None):
    """Convert an inverted abstract (a dictionary of word -> list of positions)
    to an ordered list of words representing the abstract

    :inverted_abstract: dict
    :index_length: int: the number of words in the abstract
    :returns: list

    """
    if index_length is None:
        # if the number of words is not provided, find it
        indices = set()
        for v in itervalues(inverted_abstract):
            for idx in v:
                indices.add(idx)
        index_length = max(indices) + 1

    # reverse the inverted abstract
    iabs_rev = {}
    for k, v in iteritems(inverted_abstract):
        for idx in v:
            iabs_rev[idx] = k
    # reconstruct the abstract
    abs_words = []
    for i in range(index_length):
        try:
            abs_words.append(iabs_rev[i])
        except KeyError:
            pass
    return abs_words

class GraphSearchQuery(MAGQuery):

    """Docstring for GraphSearchQuery. """

    URL = MAGConf.BASE_URL + '/graph/search?json'
    def __init__(self, json_body=None):
        """TODO: to be defined1. """
        MAGQuery.__init__(self)
        self.json_body = json_body

        self.query_type = MAGQueryType.GRAPH_TRAVERSAL

    def get_url(self):
        return self.URL

    def get_body(self):
        if not self.json_body:
            raise RuntimeError("the GraphSearch query needs a json_body")

        return self.json_body
