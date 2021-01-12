# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2019-08-28
# Gateway Version: 19.5.1 or greater
# Description: BlueCat Gateway module for Tanium API calls

import os
import sys
import requests
import json
import time
import datetime

DEFAULT_RTRY_COUNT=4
DEFAULT_INTERVAL=3

api_base = 'https://'
api_url = {
    'login': '/api/v2/session/login',
    'logout': '/api/v2/session/logout',
    'parse_question': '/api/v2/parse_question',
    'issue_question': '/api/v2/questions',
    'completeness': '/api/v2/result_info/question/{id}',
    'get_answer': '/api/v2/result_data/question/{id}'
}

questions = {
    'managed_assets' : \
    'Get Computer ID and Computer Name and '\
        'Tanium Client IP Address and MAC Address and '\
        'Manufacturer and OS Platform and '\
        'Operating System and Username '\
        'from all machines',
    'unmanaged_assets' : \
    'Get Unmanaged Assets '\
        'from all machines'
}
subnet_text ='(Tanium Client Subnet matches {subnet})'

class TaniumException(Exception): pass

class TaniumAPI(object):

    def __init__(self, server_address, ignore_ssl_validation=True, debug=False):
        self._server_address = server_address
        self._session = None
        self._verify = False if ignore_ssl_validation else True
        self._debug = debug

    def get_api_url(self, key):
        return api_base + self._server_address + api_url[key]

    def login(self, user_id, password):
        status = False
        try:
            data = {
                'username': user_id,
                'domain': '',
                'password': password
            }
            response = requests.post(self.get_api_url('login'), json=data, verify=self._verify)
            if response.status_code == 200:
                status = True
                data = response.json()['data']
                self._session = data['session']
            elif self._debug:
                print('DEBUG: Response <%s>' % str(response))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return status

    def logout(self):
        status = False
        try:
            data = {
                'session': self._session
            }
            response = requests.post(self.get_api_url('logout'), json=data, verify=self._verify)
            if response.status_code == 200:
                status = True
            elif self._debug:
                print('DEBUG: Response <%s>' % str(response))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return status

    def parse_question(self, question_text):
        question = None
        try:
            headers = { 'session': self._session }
            data = { 'text': question_text }
            response = requests.post(
                self.get_api_url('parse_question'),
                headers=headers, json=data, verify=self._verify
            )
            if response.status_code == 200:
                data = response.json()['data']
                question = data[0]
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return question

    def issue_question(self, question):
        question_id = 0
        try:
            headers = { 'session': self._session }
            response = requests.post(
                self.get_api_url('issue_question'),
                headers=headers, json=question, verify=self._verify
            )
            if response.status_code == 200:
                data = response.json()['data']
                question_id = data['id']
                status = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return question_id

    def completeness(self, id):
        completeness = 0
        try:
            headers = { 'session': self._session }
            response = requests.post(
                self.get_api_url('completeness').format(id=id),
                headers=headers, verify=self._verify
            )
            if response.status_code == 200:
                data = response.json()['data']
                result_info = data['result_infos'][0]
                completeness = 100 * result_info['mr_tested'] / result_info['estimated_total']

        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return completeness

    def get_answer(self, id):
        result_set = None
        try:
            headers = { 'session': self._session }
            response = requests.post(
                self.get_api_url('get_answer').format(id=id),
                headers=headers, verify=self._verify
            )
            if response.status_code == 200:
                data = response.json()['data']
                result_set = data['result_sets'][0]
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return result_set

    def get_with_text(self, subnets):
        with_text = ''
        length = len(subnets)
        print('length = ', length)
        if 0 < length:
            with_text += ' with '
            for i in range(length):
                with_text += subnet_text.format(subnet=subnets[i])
                if i + 1 < length:
                    with_text += ' or '
        return with_text

    def get_managed_assets(self, subnets=[], retry_count=DEFAULT_RTRY_COUNT, interval=DEFAULT_INTERVAL):
        completeness = 0
        clients = []
        question_text = questions['managed_assets']
        question_text += self.get_with_text(subnets)
        if self._debug:
            print('Question Text: <%s>' % question_text)

        question = self.parse_question(question_text)
        if question is not None:
            question_id = self.issue_question(question)
            if 0 != question_id:
                while 0 < retry_count:
                    completeness = self.completeness(question_id)
                    print('Completeness is {completeness}%'.format(completeness=int(completeness)))
                    if 90 < completeness:
                        break
                    time.sleep(interval)
                    retry_count -= 1
                result_set = self.get_answer(question_id)
                rows = result_set['rows']
                now = datetime.datetime.now()
                last_found = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                for row in rows:
                    client = {}
                    data = row['data']
                    client['managed'] = True
                    client['id'] = data[0][0]['text']
                    client['computer_name'] = data[1][0]['text']
                    client['ip_address'] = data[2][0]['text']

                    mac_addresses = []
                    for mac_address in data[3]:
                        mac_addresses.append(mac_address['text'])
                    client['mac_address'] = mac_addresses

                    client['manufacturer'] = data[4][0]['text']
                    client['os_platform'] = data[5][0]['text']
                    client['os'] = data[6][0]['text']
                    client['username'] = data[7][0]['text']
                    client['last_found'] = last_found
                    clients.append(client)
        return {'complateness': completeness, 'clients': clients}

    def _check_unknown(self, value):
        ret = ''
        if value is not None and value != 'unknown':
            ret = value
        return ret

    def get_unmanaged_assets(self, subnets=[], retry_count=DEFAULT_RTRY_COUNT, interval=DEFAULT_INTERVAL):
        completeness = 0
        clients = []
        question_text = questions['unmanaged_assets']
        question_text += self.get_with_text(subnets)
        if self._debug:
            print('Question Text: <%s>' % question_text)

        question = self.parse_question(question_text)
        if question is not None:
            question_id = self.issue_question(question)
            if 0 != question_id:
                while 0 < retry_count:
                    completeness = self.completeness(question_id)
                    print('Completeness is {completeness}%'.format(completeness=int(completeness)))
                    if 90 < completeness:
                        break
                    time.sleep(interval)
                    retry_count -= 1
                result_set = self.get_answer(question_id)
                rows = result_set['rows']
                now = datetime.datetime.now()
                last_found = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                for row in rows:
                    client = {}
                    data = row['data']
                    client['managed'] = False
                    client['id'] = data[4][0]['text'].replace('-', '')
                    client['computer_name'] = self._check_unknown(data[3][0]['text'])
                    client['ip_address'] = data[2][0]['text']

                    mac_addresses = []
                    for mac_address in data[4]:
                        mac_addresses.append(mac_address['text'])
                    client['mac_address'] = mac_addresses

                    client['manufacturer'] = ''
                    client['os_platform'] = self._check_unknown(data[5][0]['text'])
                    client['os'] = \
                        self._check_unknown(data[5][0]['text']) + ' ' + \
                        self._check_unknown(data[6][0]['text'])
                    client['username'] = ''
                    client['last_found'] = last_found
                    clients.append(client)
        return {'complateness': completeness, 'clients': clients}

    def get_client_detail_url(self, dashboard_url, client_id):
        pass
#         return dashboard_url + api_url['get_client_detail'].format(id=client_id)
