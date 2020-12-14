import unittest
import requests
import bluecat_portal.config as user_config
import json


class RestAPIUnitTests(unittest.TestCase):
    def setUp(self):
        host = getattr(user_config, 'listen_on', 'localhost')
        port = getattr(user_config, 'port', '8000')
        test_user = getattr(user_config, 'test_user', 'portal')
        test_password = getattr(user_config, 'test_password', 'portal')
        self.test_url = "http://%s:%s" % (host, port)
        r = requests.post(
            "%s/rest_login" %(self.test_url),
            headers={"Content-Type": "application/json"},
            data=json.dumps({"username": test_user, "password": test_password})
        )
        if r.status_code != 200:
            raise Exception("We cannot login to BAM")

        self.bam_token = json.loads(r.text).get('access_token', None)
        if self.bam_token is None:
            raise Exception("Invalid BAM token")


