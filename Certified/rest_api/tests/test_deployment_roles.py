import json
import unittest

import config.default_config as config
from .library.test import RestAPIUnitTests
from .library.unit_test_utils import api_req


class DeploymentOptionUnitTests(RestAPIUnitTests):

    def setUp(self):
        RestAPIUnitTests.setUp(self)
        self.default_config = config.default_configuration
        r = api_req(
            self.test_url,
            'configurations',
            self.bam_token,
            {'name': self.default_config, 'properties': ''},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test configuration')
        r = api_req(
            self.test_url,
            'configurations/%s/servers' % self.default_config,
            self.bam_token,
            {'interface_address': '192.168.100.205', 'fqdn': 'master.test-servers.com', 'friendly_name': 'test-ddimaster'},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test server')
        r = api_req(
            self.test_url,
            'configurations/%s/views' % self.default_config,
            self.bam_token,
            {'name': 'my_view', 'properties': ''},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test view')
        as_json = json.loads(r.text)
        r = api_req(
            self.test_url,
            'configurations/%s/views/my_view/zones' % self.default_config,
            self.bam_token,
            {'name': 'testing', 'properties': ''},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test zone')
        r = api_req(
            self.test_url,
            'configurations/%s/ipv4_blocks' % self.default_config,
            self.bam_token,
            {'name': 'my_block', 'address': '192.168.0.0', 'cidr_notation': '16',
             'properties': 'defaultView=%s|' % as_json['id']},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test block')
        r = api_req(
            self.test_url,
            'configurations/%s/ipv4_blocks/192.168.0.0/16/create_network' % self.default_config,
            self.bam_token,
            {'cidr': '192.168.10.0/24',
             'properties': 'Zone=INTERNAL|Service=---|Region=AMER|defaultView=%s|' % as_json['id']},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test network')

    def test_create_roles(self):
        endpoints = [
            'configurations/%s/ipv4_blocks/192.168.0.0/16/deployment_roles' % self.default_config,
            'configurations/%s/ipv4_networks/192.168.10.0/deployment_roles' % self.default_config,
            'configurations/%s/views/my_view/deployment_roles' % self.default_config,
            'configurations/%s/views/my_view/zones/testing/deployment_roles' % self.default_config
        ]
        roles = [
            {'server_fqdn': 'master.test-servers.com', 'role_type': 'dns', 'role': 'master'},
            {'server_fqdn': 'master.test-servers.com', 'role_type': 'dhcp', 'role': 'master'}
        ]
        for endpoint in endpoints:
            if 'views' in endpoint:
                r = api_req(
                    self.test_url,
                    endpoint,
                    self.bam_token,
                    roles[0],
                    'POST'
                )
                self.assertEqual(r.status_code, 201)
            else:
                for role in roles:
                    r = api_req(
                        self.test_url,
                        endpoint,
                        self.bam_token,
                        role,
                        'POST'
                    )
                    self.assertEqual(r.status_code, 201)

    def test_get_roles(self):
        endpoints = [
            'ipv4_blocks/192.168.0.0/16/deployment_roles',
            'views/my_view/deployment_roles',
            'zones/testing/deployment_roles',
            'ipv4_networks/192.168.10.0/deployment_roles'
        ]

        roles = [
            {'server_fqdn': 'master.test-servers.com', 'role_type': 'dns', 'role': 'master'},
            {'server_fqdn': 'master.test-servers.com', 'role_type': 'dhcp', 'role': 'master'}
        ]

        for endpoint in endpoints:
            for role in roles:
                if 'views' in endpoint or 'zones' in endpoint:
                    if role['role_type'] != 'dns':
                        continue
                api_req(
                    self.test_url,
                    endpoint,
                    self.bam_token,
                    role,
                    'POST'
                )
                new_end = endpoint.split('/')
                new_end.remove(new_end[-1])
                new_end = '/'.join([x for x in new_end])
                if 'views' in endpoint or 'zones' in endpoint:
                    new_end += '/server/master.test-servers.com/deployment_roles'
                else:
                    new_end += '/role_type/%s/server/master.test-servers.com/deployment_roles' % role['role_type']
                r = api_req(self.test_url, new_end, self.bam_token)
                as_json = json.loads(r.text)
                self.assertEqual(as_json['service'], role['role_type'].upper())
                self.assertEqual(r.status_code, 200)

    def tearDown(self):
        r = api_req(
            self.test_url,
            'configurations/%s' % self.default_config,
            self.bam_token,
            None,
            'DELETE'
        )
        RestAPIUnitTests.tearDown(self)


if __name__ == '__main__':
    unittest.main()
