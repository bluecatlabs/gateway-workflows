Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

  By: Xiao Dong, Anshul Sharma, Chris Storz (cstorz@bluecatnetworks.com)
  Date: 06-09-2018  
  Gateway Version: 19.8.1  
  Description: This workflow will provide access to a REST-based API for BlueCat Gateway.
               Once imported and permissioned, documentation for the various available endpoints can
               be viewed by navigating to /api/v1/. 


Known issues:
1. On upgrade or change, remove all __pycache__ folders and __*.pyc__ files as you make experience odd results as a result of caching


How to contribute:

1. Identify a use case that is currently not covered by existing endpoints. The use case should be general and not overly specific to your implementation.
2. Review the code in dns_page.py and ip_space_page.py to get a general understanding of the constructs involved. Generally there are the following elements involved in a set of endpoints:
    1. Namespaces (where the endpoints are located)
    2. Models (for ingestion of JSON)
    3. Parser (for parsing to the model)
    4. Routes & methods (actual location, actions and logic)
3. Design your endpoints to follow [REST best practices](https://www.moesif.com/blog/api-guide/api-design-guidelines/ "REST best practices")
4. Implement and test your endpoints
5. Create a pull request and outline your use case and test cases for review

Example contribution:

Use case: Get next IP in a network. This is a commonly utilized API that isn't available at the time of writing.

Design:

Two endpoints to be added, one for the default configuration, the other allows for selection of configuration and network

POST /configurations/{configuration}/ipv4_networks/{network}/get_next_ip/
POST /ipv4_addresses/{network}/get_next_network/

This follows general REST principles in hierarchy and using POST for creation actions. The specifics of the IP such as mac address, hostinfo and more will be passed as JSON using a model

Implementation:

1. Add namespace if it does not already exist. In this case, the IP4 Address namespace does not exist so it will be created. Generally the space applicable to most calls already exists.
```python
ip4_address_root_default_ns = api.namespace('ipv4_addresses', description='IPv4 Address operations')
ip4_address_root_ns = api.namespace(
    'ipv4_addresses',
    path='/configurations/<string:configuration>/ipv4_networks/',
    description='IPv4 Address operations',
)

ip4_address_default_ns = api.namespace('ipv4_addresses', description='IPv4 Address operations')
ip4_address_ns = api.namespace(
    'ipv4_addresses',
    path='/configurations/<string:configuration>/ipv4_networks/',
    description='IPv4 Address operations',
)
```

2. Add model if required. If you will be receiving JSON data and a model doesn't already exist, create an appropriate model.

```python
ip4_address_post_model = api.model(
    'ip4_address_post',
    {
        'mac_address':  fields.String(description='MAC Address value'),
        'hostinfo':  fields.String(
            description='A string containing host information for the address in the following format: '
                        'hostname,viewId,reverseFlag,sameAsZoneFlag'
        ),
        'action':  fields.String(
            description='Desired IP4 address state: MAKE_STATIC / MAKE_RESERVED / MAKE_DHCP_RESERVED'
        ),
        'properties': fields.String(description='The properties of the IP4 Address', default='attribute=value|'),
    },
)
```

3. Add parser as required.

```python
ip4_address_post_parser = reqparse.RequestParser()
ip4_address_post_parser.add_argument('mac_address', location="json", help='The MAC address')
ip4_address_post_parser.add_argument('hostinfo', location="json", help='The hostinfo of the address')
ip4_address_post_parser.add_argument('action', location="json", help='The action for address assignment')
ip4_address_post_parser.add_argument('properties', location="json", help='The properties of the record')
```

4. Implement specific endpoints underneath the namespace.

```python
@ip4_address_ns.route('/<string:network>/get_next_ip/')
@ip4_address_default_ns.route('/<string:network>/get_next_network/', defaults=config_defaults)
@ip4_address_ns.response(404, 'IPv4 address not found')
class IPv4NextIP4Address(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_address_ns.response(201, 'Next IP successfully created.', model=entity_return_model)
    @ip4_address_ns.expect(ip4_address_post_model, validate=True)
    def post(self, configuration, network):
        """
        Create the next available IP4 Address

        Network can be of the format of network address:
        1. 10.1.0.0

        """
        data = ip4_address_post_parser.parse_args()
        mac = data.get('mac_address', '')
        hostinfo = data.get('hostinfo', '')
        action = data.get('action', '')
        properties = data.get('properties', '')

        configuration = g.user.get_api().get_configuration(configuration)
        network = configuration.get_ip_range_by_ip("IP4Network", network)

        ip = network.assign_next_available_ip4_address(mac, hostinfo, action, properties)
        result = ip.to_json()

        return result, 201
```

