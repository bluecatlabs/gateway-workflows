import requests
import json

def api_req(url, uri, token, payload=None, req_type='GET'):
    full_url = "%s/api/v1/%s/" % (url, uri)
    full_url = full_url.replace('//', '/')
    full_url = full_url.replace('http:/', 'http://')

    headers = {
        'auth': "%s" % token,
        'content-type': "application/json",
        'cache-control': "no-cache"
    }

    params = {'headers':headers}
    if payload is not None:
        params['data'] = json.dumps(payload)
    r = requests.request(
        req_type,
        full_url,
        **params
    )
    return r