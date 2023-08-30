# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
from typing import Any

from requests import Session

from app_user import UserSession
from bluecat_libraries.http_client import GeneralError, ClientError
from ..common import common
from ..common.exception import UserException


class BAMAuth:
    def __init__(self, rest_endpoint_url, verify: Any = True) -> None:
        """
        ``verify`` has the same meaning as arguments of the same name commonly found in
        """
        self.rest_endpoint_url = rest_endpoint_url
        # TODO: separate class BAMCredential
        self.username = common.read_config_file('BAM_CREDENTIALS', 'username')
        self.password = common.read_config_file('BAM_CREDENTIALS', 'password')
        self.session = Session()
        self.session.verify = verify
        self.session_id = None
        if not self.inherited_session():
            self.create_session()

    def inherited_session(self):
        """
        Inherited Session from current gateway user
        """
        u = UserSession.validate(self.rest_endpoint_url, self.username, self.password)
        token = "Basic {}".format(u.get_unique_name().split(': ')[1])
        self.set_token(token)
        return token

    def create_session(self):
        """
        Create new session for BAM REST API v2.
        """
        headers = {
            'Content-Type': 'application/json',
        }

        json_data = {
            'username': self.username,
            'password': self.password
        }
        try:
            response = self.session.post(self.rest_endpoint_url + '/sessions', headers=headers, json=json_data)
        except Exception as exc:
            raise GeneralError("Connection Error") from exc
        if response.status_code == 401:
            raise ClientError("Invalid BAM credential")
        elif response.status_code == 404:
            raise UserException('BAM {} not support RESTv2'.format(self.rest_endpoint_url))

        basic_token = "Basic {}".format(response.json()['basicAuthenticationCredentials'])
        self.session_id = response.json()['id']
        self.set_token(basic_token)
        return basic_token

    def set_token(self, token):
        """
        Set token used for BAM authentication.

        :param token: Token to be used for BAM authentication.
        """
        self.session.headers.update({"Authorization": token})

    # TODO: confirmed don't need this func
    # def terminate_session(self):
    #     try:
    #         self._require_auth()
    #         data = '{"state": "TERMINATED"}'
    #         self.session.patch(self.rest_endpoint_url + '/sessions/{}'.format(self.session_id), data=data)
    #     except Exception:
    #         raise GeneralError("Connection Error")
    #     self.clear_token()

    def clear_token(self):
        """
        Clear the token used for BAM authentication.
        """
        del self.session.headers["Authorization"]
