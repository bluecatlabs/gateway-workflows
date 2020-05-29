from flask import g
from .library.models.deployment_models import deployment_option_post_model, deployment_role_post_model


def add_option(entity, data):
    on = data.get('name')
    try:
        ov = int(data.get('value'))
    except Exception as e:
        ov = data.get('value')
    properties = data.get('properties', '')

    try:
        depl_opt = g.user.get_api()._api_client.service.addDNSDeploymentOption(
            entityId=entity.get_id(),
            name=on,
            value=ov,
            properties=properties
        )
    except Exception as e:
        try:
            depl_opt = g.user.get_api()._api_client.service.addDHCPServiceDeploymentOption(
                entityId=entity.get_id(),
                name=on,
                value=ov,
                properties=properties
            )
        except Exception as e:
            depl_opt = g.user.get_api()._api_client.service.addDHCPClientDeploymentOption(
                entityId=entity.get_id(),
                name=on,
                value=ov,
                properties=properties
            )

    result = g.user.get_api().get_entity_by_id(depl_opt)
    return result.to_json(), 201


def del_option(entity, opt_name, server):
    opts, val = get_option(entity, opt_name, server)
    for opt in opts:
        if opt.get_name().lower() == opt_name.lower():
            opt.delete()

    return '', 204


def get_option(entity, opt_name, server):
    opts_to_return = []
    options = entity.get_deployment_options('DNSOption', server)
    for option in options:
        if option.get_name().lower() == opt_name.lower():
            opts_to_return.append(option.to_json())
    if len(opts_to_return) == 0:
        options = entity.get_deployment_options('DHCPServiceOption', server)
        for option in options:
            if option.get_name().lower() == opt_name.lower():
                opts_to_return.append(option.to_json())
    if len(opts_to_return) == 0:
        options = entity.get_deployment_options('DHCPV4ClientOption', server)
        for option in options:
            if option.get_name().lower() == opt_name.lower():
                opts_to_return.append(option.to_json())

    return opts_to_return, 200


def add_role(entity, data):
    primary = data.get('server_fqdn')
    secondary = data.get('secondary_fqdn', '')
    role_type = data.get('role_type')
    role = data.get('role')
    properties = data.get('properties', '')
    if not properties:
        properties = ''

    candidates = g.user.get_api().search_by_object_types(pattern=primary, types='NetworkServerInterface')
    for candidate in candidates:
        if candidate.get_name().lower() == primary.lower():
            primary = candidate.get_id()
            break

    if secondary:
        candidates = g.user.get_api().search_by_object_types(pattern=secondary, types='NetworkServerInterface')
        for candidate in candidates:
            if candidate.get_name().lower() == secondary.lower():
                secondary = candidate.get_id()
                break

    if role_type.lower() == 'dns':
        if secondary and 'zonetransserverinterface' not in properties.lower():
            properties += 'zoneTransServerInterface=%s|' % secondary

        if role.lower() not in ['master', 'slave', 'master_hidden', 'slave_stealth',
                                'forwarder', 'stub', 'recursion', 'none']:
            return 'Provided role is not supported', 404

        if entity.get_type().lower() not in ['view', 'zone']:
            if 'view=' not in properties.lower():
                properties += 'view=%s|' % entity.get_property('defaultView')

        added_role = g.user.get_api()._api_client.service.addDNSDeploymentRole(
            entityId=entity.get_id(),
            type=role.upper(),
            properties=properties,
            serverInterfaceId=primary,
        )
        result = g.user.get_api().get_entity_by_id(added_role)
        return result.to_json(), 201
    elif role_type.lower() == 'dhcp':
        if secondary and 'secondaryserverinterfaceid' not in properties.lower():
            properties += 'secondaryServerInterfaceId=%s|' % secondary

        if role.lower() not in ['master', 'none'] or entity.get_type().lower() not in ['ip4network', 'ip4block']:
            return 'Provided role is not supported', 404

        added_role = g.user.get_api()._api_client.service.addDHCPDeploymentRole(
            entityId=entity.get_id(),
            type=role.upper(),
            properties=properties,
            serverInterfaceId=primary
        )
        result = g.user.get_api().get_entity_by_id(added_role)
        return result.to_json(), 201


def del_role(entity, role_type, server):
    role, ret_val = get_role(entity, role_type, server)
    role = g.user.get_api().get_entity_by_id(role['id'])
    role.delete()
    return '', 204


def get_role(entity, role_type, server):
    candidates = g.user.get_api().search_by_object_types(pattern=server, types='NetworkServerInterface')
    for candidate in candidates:
        if candidate.get_name().lower() == server.lower():
            server = candidate.get_id()
            break

    if role_type.lower() == 'dhcp':
        result = g.user.get_api()._api_client.service.getDHCPDeploymentRole(
            entityId=entity.get_id(),
            serverInterfaceId=server
        )
        return result, 200
    elif role_type.lower() == 'dns':
        result = g.user.get_api()._api_client.service.getDNSDeploymentRole(
            entityId=entity.get_id(),
            serverInterfaceId=server
        )
        return result, 200
