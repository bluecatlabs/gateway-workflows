import json
import unittest

import config.default_config as config
from .library.test import RestAPIUnitTests
from .library.unit_test_utils import api_req


class IP4BlocksUnitTests(RestAPIUnitTests):

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
            raise Exception('We were unable to create the needed test configuration!')

    def test_create_block(self):
        endpoints = [
            'configurations/' + self.default_config + '/ipv4_blocks',
            'configurations/' + self.default_config + '/ipv4_blocks/192.168.0.0/8/ipv4_blocks',
            'ipv4_blocks/192.168.0.0/16/ipv4_blocks',
            'ipv4_blocks'
        ]
        cidrs = ['16', '18', '19', '20']
        for cidr, endpoint in zip(cidrs, endpoints):
            r = api_req(
                self.test_url,
                endpoint,
                self.bam_token,
                {'name': 'my_block', 'address': '192.168.0.0', 'cidr_notation': cidr, 'properties': ''},
                'POST'
            )
            self.assertEqual(r.status_code, 201)

    def test_get_block(self):
        address, cidr = '100.0.0.0', '16'
        endpoints = [
            '/configurations/' + self.default_config + '/ipv4_blocks/' + address + '/' + cidr,
            '/ipv4_blocks/' + address + '/' + cidr
        ]

        api_req(
            self.test_url,
            'ipv4_blocks',
            self.bam_token,
            {'name': 'my_get_block', 'address': address, 'cidr_notation': cidr, 'properties': ''},
            'POST'
        )

        for endpoint in endpoints:
            r = api_req(self.test_url, endpoint, self.bam_token)
            as_json = json.loads(r.text)
            self.assertEqual(as_json['name'], 'my_get_block')
            self.assertEqual(r.status_code, 200)

    def test_get_blocks(self):
        addresses, cidrs = ['10.0.0.0', '10.0.0.0', '69.0.0.0', '8.0.0.0'], ['16', '20', '20', '21']
        endpoints = [
            'configurations/' + self.default_config + '/ipv4_blocks',
            'ipv4_blocks',
            'configurations/' + self.default_config + '/ipv4_blocks/10.0.0.0/16/ipv4_blocks',
            'ipv4_blocks/10.0.0.0/16/ipv4_blocks',
        ]
        for a, c in zip(addresses, cidrs):
            api_req(
                self.test_url,
                'ipv4_blocks',
                self.bam_token,
                {'name': 'my_get_block', 'address': a, 'cidr_notation': c, 'properties': ''},
                'POST'
            )

        for endpoint in endpoints:
            r = api_req(self.test_url, endpoint, self.bam_token)
            as_json = json.loads(r.text)
            self.assertEqual(as_json[0]['name'], 'my_get_block')
            self.assertEqual(r.status_code, 200)

    def tearDown(self):
        r = api_req(
            self.test_url,
            'configurations/' + self.default_config,
            self.bam_token,
            None,
            "DELETE"
        )
        RestAPIUnitTests.tearDown(self)


if __name__ == '__main__':
    unittest.main()
