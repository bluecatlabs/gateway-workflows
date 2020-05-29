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
            'configurations/%s/views' % self.default_config,
            self.bam_token,
            {'name': 'my_view', 'properties': ''},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test view')
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
            {'name': 'my_block', 'address': '192.168.0.0', 'cidr_notation': '16', 'properties': ''},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test block')
        r = api_req(
            self.test_url,
            'configurations/%s/ipv4_blocks/192.168.0.0/16/create_network' % self.default_config,
            self.bam_token,
            {'cidr': '192.168.10.0/24', 'properties': 'Zone=INTERNAL|Service=---|Region=AMER|'},
            'POST'
        )
        if r.status_code != 201:
            raise Exception('We are unable to create the needed test network')

    def test_create_options(self):
        # Post
        endpoints = [
            'configurations/%s/deployment_options' % self.default_config,
            'configurations/%s/ipv4_blocks/192.168.0.0/16/deployment_options' % self.default_config,
            'configurations/%s/ipv4_networks/192.168.10.0/deployment_options' % self.default_config,
            'configurations/%s/views/my_view/deployment_options' % self.default_config,
            'configurations/%s/views/my_view/zones/testing/deployment_options' % self.default_config
        ]
        options = [
            {'name': 'allow-ddns', 'value': 'any', 'properties': ''},
            {'name': 'dns-server', 'value': '8.8.8.8', 'properties': ''},
            {'name': 'client-updates', 'value': 'true', 'properties': ''}
        ]
        for endpoint in endpoints:
            if 'views' in endpoint or 'zones' in endpoint:
                r = api_req(
                    self.test_url,
                    endpoint,
                    self.bam_token,
                    options[0],
                    'POST'
                )
                self.assertEqual(r.status_code, 201)
            else:
                for option in options:
                    r = api_req(
                        self.test_url,
                        endpoint,
                        self.bam_token,
                        option,
                        'POST'
                    )
                    self.assertEqual(r.status_code, 201)

    def test_get_options(self):
        endpoints = [
            'configurations/%s/deployment_options' % self.default_config,
            'ipv4_blocks/192.168.0.0/16/deployment_options',
            'views/my_view/deployment_options',
            'zones/testing/deployment_options',
            'ipv4_networks/192.168.10.0/deployment_options'
        ]

        options = [
            [{'name': 'allow-xfer', 'value': 'any', 'properties': ''}, 'DNS'],
            [{'name': 'ping-check', 'value': 'true', 'properties': ''}, 'DHCPService'],
            [{'name': 'domain-name', 'value': 'example.com', 'properties': ''}, 'DHCPClient']
        ]

        for endpoint in endpoints:
            for option in options:
                if 'views' in endpoint or 'zones' in endpoint:
                    if option[0]['name'] != 'allow-xfer':
                        continue
                api_req(
                    self.test_url,
                    endpoint,
                    self.bam_token,
                    option[0],
                    'POST'
                )
                new_end = endpoint.split('/')
                new_end.remove(new_end[-1])
                new_end = '/'.join([x for x in new_end])
                new_end += '/option_name/%s/server/0/deployment_options' % option[0]['name']
                r = api_req(self.test_url, new_end, self.bam_token)
                as_json = json.loads(r.text)
                self.assertEqual(as_json[0]['type'], option[1])
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
