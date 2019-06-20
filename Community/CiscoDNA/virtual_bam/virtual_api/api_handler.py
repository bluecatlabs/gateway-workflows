from flask import make_response, json

JSON_MIME_TYPE = 'application/json'

views_file = 'data/views.txt'
bluecat_api_list = 'data/session_response.txt'
deployment_roles_file = 'data/deployment_roles.txt'
pools_file = 'data/pools.txt'
network_interfaces_file = 'data/network_interfaces.txt'
client_options_file = 'data/client_options.txt'
servers_file = 'data/servers.txt'
ip_address_file = 'data/ip_address.txt'

users = {
	'tokenkey': 'auth',
	'tokenvalue': 'Basic 2ME0v//+oOsioQhdY8Hg93Mw7qu1IbX0gk89MV/uUzrSY2bALk/AjStm1eDtlkJHrvL29Lhp2CKBaE75Iy6Aow=='
}


entity_by_name_users = {
	"id": 100880,
	"name": "gateway-user",
	"type": "User",
	"properties": "PortalGroup=all|email=automation@tma.com.vn|userType=ADMIN|userAccessType=GUI_AND_API|"
}


system_info = "hostName=automation|version=8.3.0-128.GA.bcn|address=localhost|" \
		              "clusterRole=PRIMARY|replicationRole=PRIMARY|replicationStatus=OFF|" \
		              "entityCount=100752|databaseSize=59.34MB|loggedInUsers=1|"


def json_response(data='', status=200, headers=None):
	headers = headers or {}
	if 'Content-Type' not in headers:
		headers['Content-Type'] = JSON_MIME_TYPE
	return make_response(data, status, headers)


def read_file(file_name):
	content = ''
	f = open(file_name, "r")
	f1 = f.readlines()
	for line in f1:
		content = content + line
	f.close()
	return content


def get_view(view):
	list = json.loads(read_file(views_file))
	for item in list:
		name = item['name']
		if name == view:
			return item
	return {
		"id": 0,
		"name": None,
		"type": None,
		"properties": None
	}


def get_pools_under_id(parentId, type):
	pools = []
	list = json.loads(read_file(pools_file))
	for item in list:
		parent = item['parentId']
		itype = item['type']
		if parent == parentId and itype == type:
			pools.append(item)
	return pools


def get_object_by_entityid(file_name, entity_id):
	servers = []
	list = json.loads(read_file(file_name))
	for item in list:
		if item['entityId'] == entity_id:
			servers.append(item)
	return servers


def get_entity_by_id(id):
	files = [deployment_roles_file, pools_file, views_file,
	         network_interfaces_file, client_options_file, servers_file,
	         ip_address_file]
	for file in files:
		list = json.loads(read_file(file))
		for item in list:
			if item['id'] == id:
				return item
			

def get_ip_address(ip):
	list = json.loads(read_file(ip_address_file))
	for item in list:
		property = item['properties']
		address = property.split('|')[0].split('=')[1]
		if address == ip:
			return item
	return {
        "id": 0,
        "name": None,
        "type": None,
        "properties": None
	}
