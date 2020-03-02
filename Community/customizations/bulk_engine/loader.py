from flask import g


def load(data, **kwargs):
    # Global variables
    default_configuration, default_view = get_defaults(kwargs)
    globals = {
        "on_fail": kwargs.get('on_fail', 'abort')
    }

    results = {}

    if data.get('networks') is not None:
        results['networks'] = load_networks(data['networks'], default_configuration, **globals)

    if data.get('ip_addresses') is not None:
        results['ip_addresses'] = load_ips(data['ip_addresses'], default_configuration, **globals)

    if data.get('dns_records') is not None:
        results['dns_records'] = load_records(data['dns_records'], default_configuration, default_view, **globals)

    return results


def load_records(data, configuration, view, **kwargs):
    results = {}
    for record in data:
        c, v = get_configuration_objects(record, configuration, view)
        failed = False
        if record.get('action') == 'ADD':
            try:
                if record['type'] == 'A':
                    new_record = v.add_host_record('%s.%s' % (record['record'], record['zone']), [record['address']])
                elif record['type'] == 'C':
                    new_record = v.add_alias_record('%s.%s' % (record['record'], record['zone']), record['linked_fqdn'])

                results[record['record'] + "." + record['zone']] = str(new_record.get_id())
            except Exception as e:
                message = str(e)
                failed = True
        elif record.get('action') == 'DEL':
            try:
                if record['type'] == 'A':
                    existing_record = v.get_host_record(record['record'] + "." + record['zone'])
                if record['type'] == 'C':
                    existing_record = v.get_alias_record(record['record'] + "." + record['zone'])

                existing_record.delete()
                results[record['record'] + "." + record['zone']] = 'deleted'
            except Exception as e:
                message = str(e)
                failed = True
        if failed:
            recourse = record.get('on_fail', kwargs.get('on_fail')) # local, global, default of abort
            results[record['record'] + "." + record['zone']] = message
            if recourse == 'abort':
                break

    return results


def load_ips(data, configuration, **kwargs):
    results = {}
    for ip in data:
        c = get_configuration_objects(ip, configuration)
        failed = False
        if ip.get('action') == 'ADD':
            try:
                parent_network = c.get_ip_range_by_ip("IP4Network", ip['address'])
                new_ip = parent_network.assign_ip4_address(ip["address"], "", "", "MAKE_STATIC")
                results[ip['address']] = str(new_ip.get_id())
            except Exception as e:
                message = str(e)
                failed = True
        elif ip.get('action') == 'DEL':
            try:
                existing_ip = c.get_ip4_address(ip['address'])
                existing_ip.delete()
                results[ip['address']] = 'deleted'
            except Exception as e:
                message = str(e)
                failed = True
        if failed:
            recourse = ip.get('on_fail', kwargs.get('on_fail')) # local, global, default of abort
            results[ip['address']] = message
            if recourse == 'abort':
                break

    return results


def load_networks(data, configuration, **kwargs):
    results = {}
    for network in data:
        c = get_configuration_objects(network, configuration)
        failed = False
        if network.get('action') == 'ADD':
            try:
                name = network.get('name', '')
                parent_block = c.get_ip_range_by_ip("IP4Block", network['address'])
                new_network = parent_block.add_ip4_network("%s/%s" % (network['address'], network['cidr']), 'name=%s'%name)
                results[network['address'] + '/' + network['cidr']] = str(new_network.get_id())
            except Exception as e:
                message = str(e)
                failed = True
        elif network.get('action') == 'DEL':
            try:
                existing_network = c.get_ip_range_by_ip("IP4Network", network['address'])
                existing_network.delete()
                results[network['address'] + '/' + network['cidr']] = 'deleted'
            except Exception as e:
                message = str(e)
                failed = True
        if failed:
            recourse = network.get('on_fail', kwargs.get('on_fail')) # local, global, default of abort
            results[network['address'] + '/' + network['cidr']] = message
            if recourse == 'abort':
                break

    return results


def get_configuration_objects(data, config, view=None):
    if data.get('configuration') is not None:
        c = g.user.get_api().get_configuration(data.get('configuration'))
    else:
        c = config
    if data.get('view') is not None:
        v = c.get_view(data.get('view'))
    else:
        v = view
    if v is None:
        return c
    return c, v


def get_defaults(args):
    c, v = args.get('configuration'), args.get('view')
    config = g.user.get_api().get_configuration(c) if c is not None else None
    view = config.get_view(v) if None not in (v, c) else None
    return config, view

