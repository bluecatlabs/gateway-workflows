from REST import REST, compat
from copy import deepcopy
from collections import OrderedDict
from .utilities import *
from robot.api.deco import keyword
from requests.packages.urllib3 import disable_warnings
if compat.IS_PYTHON_2:
    from urlparse import parse_qsl, urlparse
else:
    from urllib.parse import parse_qsl, urlparse

###############################
class ExtendedRESTLibrary(REST):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def __init__(self, url=None,
                 ssl_verify=False,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent="Bluecat_RESTinstance",
                 proxies={},
                 schema={},
                 spec={},
                 instances=[]):
        self.request = {
            'method': None,
            'url': None,
            'scheme': "",
            'netloc': "",
            'path': "",
            'query': {},
            'body': None,
            'headers': {
                'Accept': REST._input_string(accept),
                'Content-Type': REST._input_string(content_type),
                'User-Agent': REST._input_string(user_agent)
            },
            'proxies': REST._input_object(proxies),
            'timeout': [None, None],
            'cert': None,
            'sslVerify': REST._input_ssl_verify(ssl_verify),
            'allowRedirects': True
        }
        if url:
            url = REST._input_string(url)
            if url.endswith('/'):
                url = url[:-1]
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            url_parts = urlparse(url)
            self.request['scheme'] = url_parts.scheme
            self.request['netloc'] = url_parts.netloc
            self.request['path'] = url_parts.path
        if not self.request['sslVerify']:
            disable_warnings()
        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": url,
            "description": None,
            "default": True,
            "examples": [],
            "type": "object",
            "properties": {
                "request": {
                    "type": "object",
                    "properties": {}
                },
                "response": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        self.schema.update(self._input_object(schema))
        self.spec = {}
        self.spec.update(self._input_object(spec))
        self.instances = self._input_array(instances)

    @keyword
    def get_body_response(self, method, endpoint, query=None):
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = method
        request['query'] = OrderedDict()
        query_in_url = OrderedDict(parse_qsl(urlparse(endpoint).query))
        if query:
            request['body'] = self.input(query)
        if query_in_url:
            request['query'].update(query_in_url)
            endpoint = endpoint.rsplit('?', 1)[0]
        return self._request(endpoint, request)['response']['body']


##### AUTHENTICATION ######
    @keyword
    def set_headers(self, headers):
        self.request['headers'].update(self._input_object(headers))