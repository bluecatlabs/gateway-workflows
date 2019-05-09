import os

from flask import Flask
from flask_restful import Api
from virtual_api.vapi import session, login, get_system_info, get_entity_by_name, get_entities, deployment_roles, \
    entity_by_id, deployment_options, add_entity, add_ip4_block_by_cidr, add_dhcp_deployment_role, \
    add_dhcp_client_deployment_option, add_view, add_dns_deployment_role, add_ip6_block_by_prefix, \
    add_ip6_address, add_ip6_network, add_ip4_network, delete, add_dhcp6_client_deployment_option, get_ip6_address, \
    get_ip4_address, assign_ip4_address

app = Flask(__name__)
api = Api(app)

if __name__ == '__main__':
    api.add_resource(session, "/Services/REST/application.wadl")
    api.add_resource(login, "/Services/REST/v1/login")
    api.add_resource(get_system_info, "/Services/REST/v1/getSystemInfo")
    api.add_resource(get_entity_by_name, "/Services/REST/v1/getEntityByName")
    api.add_resource(get_entities, "/Services/REST/v1/getEntities")
    api.add_resource(deployment_roles, "/Services/REST/v1/getDeploymentRoles")
    api.add_resource(entity_by_id, "/Services/REST/v1/getEntityById")
    api.add_resource(deployment_options, "/Services/REST/v1/getDeploymentOptions")
    api.add_resource(add_entity, "/Services/REST/v1/addEntity")
    api.add_resource(add_ip4_block_by_cidr, "/Services/REST/v1/addIP4BlockByCIDR")
    api.add_resource(add_ip6_block_by_prefix, "/Services/REST/v1/addIP6BlockByPrefix")
    api.add_resource(add_dhcp_deployment_role, "/Services/REST/v1/addDHCPDeploymentRole")
    api.add_resource(add_view, "/Services/REST/v1/addView")
    api.add_resource(add_dns_deployment_role, "/Services/REST/v1/addDNSDeploymentRole")
    api.add_resource(add_dhcp_client_deployment_option, "/Services/REST/v1/addDHCPClientDeploymentOption")
    api.add_resource(add_dhcp6_client_deployment_option, "/Services/REST/v1/addDHCP6ClientDeploymentOption")
    api.add_resource(delete, "/Services/REST/v1/delete")
    api.add_resource(add_ip4_network, "/Services/REST/v1/addIP4Network")
    api.add_resource(add_ip6_network, "/Services/REST/v1/addIP6NetworkByPrefix")
    api.add_resource(add_ip6_address, "/Services/REST/v1/addIP6Address")
    api.add_resource(get_ip4_address, "/Services/REST/v1/getIP4Address")
    api.add_resource(get_ip6_address, "/Services/REST/v1/getIP6Address")
    api.add_resource(assign_ip4_address, "/Services/REST/v1/assignIP4Address")
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 7000))
    app.run(host=host, port=port)
