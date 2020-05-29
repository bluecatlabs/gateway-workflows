import json
import unittest

import config.default_config as config
from .library.test import RestAPIUnitTests
from .library.unit_test_utils import api_req


class ConfigurationUnitTests(RestAPIUnitTests):
    default_config = config.default_configuration

    def test_get_configurations(self):
        r = api_req(self.test_url, 'configurations', self.bam_token)
        self.assertEqual(r.status_code, 200)
        as_json = json.loads(r.text)
        if len(as_json) > 0:
            self.assertEqual(int, type(as_json[0]['id']))
            self.assertEqual('Configuration', as_json[0]['type'])

    def test_post_get_delete_configuration(self):
        # Post
        r = api_req(
            self.test_url,
            'configurations',
            self.bam_token,
            {'name': self.default_config, 'properties': ''},
            'POST'
        )
        self.assertEqual(r.status_code, 201)
        as_json = json.loads(r.text)
        if len(as_json) > 0:
            self.assertEqual(int, type(as_json['id']))
            self.assertEqual('Configuration', as_json['type'])

        # Get
        r = api_req(
            self.test_url,
            'configurations/' + self.default_config,
            self.bam_token
        )
        self.assertEqual(r.status_code, 200)
        as_json = json.loads(r.text)
        if len(as_json) > 0:
            self.assertEqual(int, type(as_json['id']))
            self.assertEqual('Configuration', as_json['type'])

        # Delete
        r = api_req(
            self.test_url,
            'configurations/' + self.default_config,
            self.bam_token,
            None,
            "DELETE"
        )
        self.assertEqual(r.status_code, 204)

        # Verify Delete
        r = api_req(
            self.test_url,
            'configurations/' + self.default_config,
            self.bam_token
        )
        self.assertEqual(r.status_code, 500)


if __name__ == '__main__':
    unittest.main()
