import urllib
import requests


def query(entry_point='/', method='get', baseurl=None, **kwargs):

    q = getattr(requests, method)
    url = 'http://localhost:8000{}'.format(entry_point)

    headers = {}
    if 'HTTP_AUTHORIZATION' in kwargs:
        headers['Authorization'] = kwargs['HTTP_AUTHORIZATION']

    params = kwargs.get('params', None)
    if params:
        url += '?{}'.format(urllib.parse.urlencode(params))

    if method == 'get':
        response = q(url, headers=headers)
    else:
        json_data = kwargs.get('json', {})
        response = q(url, json=json_data, headers=headers)

    if kwargs.get('response', False):
        return response
    else:
        return response.json()


def get(*args, **kwargs):
    return query(*args, method='get', **kwargs)


def post(*args, **kwargs):
    return query(*args, method='post', **kwargs)


def mock_query(client):

    def test_query(modname, entry_point='/', method='get', baseurl=None, **kwargs):
        url = '/{}{}'.format(modname, entry_point)
        params = kwargs.get('params', None)
        if params:
            url += '?{}'.format(urllib.parse.urlencode(params))

        q = getattr(client, method)

        if method == 'get':
            response = q(url, format='json')
        else:
            json_data = kwargs.get('json', {})
            response = q(url, data=json_data, format='json')

        if kwargs.get('response', False):
            return response
        else:
            return response.json()

    global query
    query = test_query