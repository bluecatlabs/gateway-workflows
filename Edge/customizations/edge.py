# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import requests

def auth(func):
    def wrapper(self, *args, **kwargs):
        if self._edge__token is None:
            return None

        return func(self, *args, **kwargs)
    return wrapper

class edge:

    __token = None
    __host = None
    __logger = None


    def __init__(self, host, client_id, client_secret, logger=None):
        self.__host = host
        self.__get_token_with_api_key(client_id, client_secret)
        self.__logger = logger


    def get_session_status(self):
        if self.__token  is None:
            return False
        else:
            return True


    @auth
    def make_new_domain_list(self, name, description):
        url = self.__host+'/v1/api/list/dns'
        headers = self.__make_headers(Accept="*/*", ContentType="application/json", AcceptEncoding="gzip, deflate")
        payload = "{\n   \"name\": \"%s\",\n   \"description\": \"%s\",\n   \"sourceType\": \"user\"\n}," \
                  % (name, description)

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            parsed_reply = json.loads(response.text)
        except:
            self.log("We were unable to complete the request", True)
            return None

        return(parsed_reply)


    @auth
    def push_file(self, id, filename ):
        url = self.__host+'/v1/api/list/dns/%s/attachfile' % id
        headers = self.__make_headers()

        try:
            file_info = {
                "file":open(filename,'rb')
            }
        except:
            self.log("We were unable to open the file %s" % filename, True)
            return None
        try:
            response = requests.request("POST", url, files=file_info, headers=headers)
            parsed_reply = json.loads(response.text)
        except:
            self.log("We were unable to complete the request", True)
            return None

        return(parsed_reply)


    @auth
    def list_dl(self):
        url = self.__host + '/v1/api/list/dns'
        headers = self.__make_headers()

        try:
            response = requests.request("GET", url, headers=headers)
            parsed_reply = json.loads(response.text)
        except:
            self.log("We were unable to complete the request", True)
            return None
        return(parsed_reply)


    @auth
    def list_read(self, domainListId):
        url = self.__host + '/v1/api/list/dns/' + domainListId
        headers = {"Authorization": "Bearer " + self.__token}
        try:
            response = requests.request("GET", url, headers=headers)
            parsed_reply = response.content.decode()
        except:
            self.log("We were unable to complete the request", True)
            return None
        return(parsed_reply)


    @auth
    def create_new_policy(self, name):
        url = self.__host + '/v1/api/list/dns'

        headers = self.__make_headers(ContentType="application/json")

        payload = "{" + f'"name":"{name}",' + "" + '"description":"", "sourceType":"user"' + "}"
        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            parsed_reply = json.loads(response.text)
        except:
            self.log("We were unable to complete the request", True)
            return None
        try:
            id = parsed_reply['id']
        except:
            self.log("We were unable to parse the id from the reply", True)
            return None
        return id


    def __get_token_with_api_key(self, client_id, client_secret):
        url = self.__host + '/v1/api/authentication/token'
        payload = \
        {
            "grantType": "ClientCredentials",
            "clientCredentials": {
                "clientId": client_id,
                "clientSecret": client_secret
            }
        }
        headers = { "Content-type": "application/json" }
        try:
            response = requests.post(url, json=payload, headers=headers)
            as_json = json.loads(response.text)
        except:
            return
        if "code" not in as_json:
            self.__token = (as_json['accessToken'])
        elif as_json["code"] != "INVALID_TOKEN":
            self.log("Our Token isn't valid", True)
        return


    def log(self, message, error=None):
        if self.__logger is not None:
            if error is None:
                self.__logger.info(message)
            else:
                self.__logger.error(message)
        else:
            print(message)


    def __make_headers(self, **kwargs):
        headers = {
            "Authorization": "Bearer %s" % self.__token
        }
        if 'ContentType' in kwargs:
            kwargs['Content-Type'] = kwargs['ContentType']
            del kwargs['ContentType']
        if 'AcceptEncoding' in kwargs:
            kwargs['Accept-Encoding'] = kwargs['AcceptEncoding']
            del kwargs['AcceptEncoding']

            headers.update(kwargs)
        return headers

