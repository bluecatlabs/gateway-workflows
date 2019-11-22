#
# Copyright (c) 2015 Aruba Networks, Inc.
# Copyright (c) 2016 Hewlett Packard Enterprise Development LP
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
#
# Forked from: https://github.com/aruba/clearpass-api-python/blob/master/clearpass/api.py

from requests import Request, Session
from time import time
from urllib.parse import urljoin, urlparse, urlunparse
from json.decoder import JSONDecodeError
#from urlparse import urljoin, urlparse, urlunparse

_session = Session()

class ConfigurationException(Exception):
	"""Exception thrown indicating there is a configuration issue preventing the API call."""
	pass

class Error(Exception):
	"""Exception thrown when an API call fails (400 or higher status code).

	The 'details' member variable contains full information about the problem.
	"""
	def __init__(self, message, code, details):
		self.message = message
		self.code = code
		self.details = details

	def __str__(self):
		return self.message + ', details: ' + repr(self.details)

class Client:
	"""API client for calling ClearPass REST/RPC API methods and handling OAuth2
	authentication.

	You MUST configure the 'host' member variable and one of the following
	for authorization:

	 - access_token (if you already performed OAuth2 authentication)
	 - client_id, client_secret (implies grant_type=client_credentials)
	 - client_id, username, password (implies grant_type=password, public client)
	 - client_id, client_secret, username, password (implies grant_type=password)

	Call the get(), post(), patch(), put(), or delete() methods to invoke the
	corresponding API calls.  OAuth2 authorization will be handled automatically
	using this method.

	To make an API call without the Authorization: header, use the invoke() method.
	"""
	def __init__(self, host='', timeout=60, insecure=False, verbose=False, debug=False,
				 access_token=None, client_id=None, client_secret=None, username=None, password=None):
		self.host = host
		self.timeout = timeout
		self.insecure = insecure
		self.verbose = verbose
		self.debug = debug  # TODO: self.debug does nothing
		self.token_type = 'Bearer'
		self.access_token = access_token
		self.access_token_expires = None
		self.client_id = client_id
		self.client_secret = client_secret
		self.username = username
		self.password = password

	def get(self, url, query_params=None):
		return self.invoke('GET', url, query_params)

	def post(self, url, body=None, query_params=None):
		return self.invoke('POST', url, query_params, body)

	def patch(self, url, body=None, query_params=None):
		return self.invoke('PATCH', url, query_params, body)

	def put(self, url, body=None, query_params=None):
		return self.invoke('PUT', url, query_params, body)

	def delete(self, url, query_params=None):
		return self.invoke('DELETE', url, query_params)

	def invoke(self, method, uri, query_params=None, body=None, authz=True):
		headers = {}
		if authz:
			headers['Authorization'] = self.authorizationHeader()
		url = self.getUrl(uri)
		if self.verbose:
			prep = _session.prepare_request(Request(method=method, url=url, params=query_params,
				headers=headers, data={}, json=body))
			print((prep.method, prep.path_url))
			if prep.headers:
				for name, value in list(prep.headers.items()):
					print(('%s: %s' % (name, value)))
			print()
			if prep.body:
				print((prep.body))
			print()
		response = _session.request(method, url, params=query_params,
			headers=headers, json=body, timeout=self.timeout, verify=not self.insecure)
		if self.verbose:
			print (('HTTP/1.1', response.status_code, response.reason))
			if response.headers:
				for name, value in list(response.headers.items()):
					print(('%s: %s' % (name, value)))
			print()
			if response.content:
				print((response.content))
			print()
		if response.status_code >= 400:
			if 'json' in response.headers['Content-Type']:
				details = response.json()
			else:
				details = response.content
			raise Error(response.reason, response.status_code, details)
		try:
			return response.json()
		except JSONDecodeError:
			return True
		
	def getUrl(self, url):
		if self.host == '':
			raise ConfigurationException('Hostname must be provided')
		rel = urlparse(url)
		path = rel.path
		if len(path):
			if path[0] != '/':
				path = '/' + path
			if path[0:4] != '/api':
				path = '/api' + path
		return urljoin('https://' + self.host, urlunparse((rel.scheme, rel.netloc, path, rel.params, rel.query, rel.fragment)))

	def authorizationHeader(self):
		if not self.access_token:
			if self.client_id and self.username and self.password:
				data = {'grant_type': 'password', 'client_id': self.client_id, 'username': self.username, 'password': self.username}
				if self.client_secret:
					data['client_secret'] = self.client_secret
			elif self.client_id and self.client_secret:
				data = {'grant_type': 'client_credentials', 'client_id': self.client_id}
				if self.client_secret:
					data['client_secret'] = self.client_secret
			else:
				raise ConfigurationException('Cannot authenticate: need (client_id, client_secret) or (client_id, username, password)')
			oauth = self.invoke('POST', '/oauth', None, data, False)
			self.token_type = oauth['token_type']
			self.access_token = oauth['access_token']
			self.access_token_expires = time() + oauth['expires_in']
		return self.token_type + ' ' + self.access_token
