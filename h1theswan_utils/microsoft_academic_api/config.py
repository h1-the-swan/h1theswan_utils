import os

class MAGConf(object):
    BASE_URL = 'https://westus.api.cognitive.microsoft.com/academic/v1.0'
    SUBSCRIPTION_KEY = os.environ['MICROSOFT_ACADEMIC_KEY']
    EVALUATE_QUERY_DEFAULTS = {
            'attributes': '*',
            'count': 50,
            'offset': 0,
            'model': 'latest'
    }
    INTERPET_QUERY_DEFAULTS = {
            'complete': 0,
            'count': 10,
            'offset': 0,
            'timeout': 1000,
            'model': 'latest'
    }
