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


from flask import render_template, flash, g, json
from bluecat import route, util
import config.default_config as config
from main_app import app
from .cache_example_form import GenericFormTemplate
import os, time


@route(app, '/cache_example/cache_example_endpoint')
@util.workflow_permission_required('cache_example_page')
@util.exception_catcher
def cache_example_cache_example_page():
    form = GenericFormTemplate()
    form.configuration.choices = get_configs(True)
    return render_template(
        'cache_example_page.html',
        ips={},
        form=form,
        text=util.get_text(_module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/cache_example/form', methods=['POST'])
@util.workflow_permission_required('cache_example_page')
@util.exception_catcher
def cache_example_cache_example_page_form():
    form = GenericFormTemplate()
    form.configuration.choices = get_configs(True)
    ips = get_ip_network_records(form.configuration.data, form.ip_network.data)

    return render_template(
        'cache_example_page.html',
        ips=ips,
        form=form,
        text=util.get_text(_module_path(), config.language),
        options=g.user.get_options(),
    )


def get_ip_network_records(conf, network_cidr):
    cache_file_name = str(conf)+"-"+network_cidr+".json"

    cached_results = read_cache(cache_file_name, 600)
    if len(cached_results) > 0:
        print(cached_results)
        return cached_results


    configuration = g.user.get_api().get_entity_by_id(conf)
    try:
        network = configuration.get_ip_range_by_ip("IP4Network", network_cidr)
    except Exception as e:
        flash(e)
        network = None
    return_ips = {}
    if network is not None:
        ips = network.get_children_of_type("IP4Address")

        for ip in ips:
            records = ip.get_linked_entities("HostRecord")
            ip_records = {}
            for record in records:
                ip_records[record.get_id()] = record.get_full_name()
            return_ips[ip.get_address()] = ip_records
    cache_it(return_ips, cache_file_name)
    return return_ips


def get_configs(cached=False):
    cache = False
    if cached:
        configs = read_cache("configurations.json", 120)
        if len(configs) != 0:
            cache=True
    if cache == False:
        configs = util.get_configurations(default_val=True)
        cache_it(configs, "configurations.json")
    return configs


def cache_it(cache, filename, location='cache', create_location=True):
    full_path = location
    if location[:5] == "cache":
        path = os.path.dirname(os.path.abspath(__file__))
        full_path = path + "/" + location + "/" + filename
    _save_data(full_path, cache, create_location)


def read_cache(filename, exp=0, location='cache'):
    full_path = location + "/" + filename
    if location[:5] == "cache":
        path = os.path.dirname(os.path.abspath(__file__))
        full_path = path + "/" + location + "/" + filename
    return _get_file(full_path, exp)






def _module_path():
    return os.path.dirname(os.path.abspath(__file__))


def _file_age(filepath):
    return time.time() - os.path.getmtime(filepath)


def _save_data(file, data, create=False):
    try:
        if create:
            with open(file, 'w+') as f:
                json.dump(data, f, sort_keys=True, indent=4)
        else:
            with open(file, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4)
    except Exception as e:
        print(e)
        print("Failed to save")
    return


def _get_file(file, exp=0):
    print(file)
    try:
        seconds = int(_file_age(file))
        if exp != 0 and seconds > exp:
            return {}
    except Exception as e:
        print(e)
    try:
        with open(file, 'r') as f:

            datastore = json.load(f)
    except:
        datastore = {}
    return datastore



