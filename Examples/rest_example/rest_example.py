# Copyright 2017 BlueCat Networks. All rights reserved.

from flask import request, g, jsonify

from bluecat import route, util
from main_app import app

# application config


#
# Example rest GET call
#
@route(app, '/rest_example/get_test')
@util.rest_workflow_permission_required('rest_example')
@util.rest_exception_catcher
def rest_get_test():
    # are we authenticated?
    # yes, build a simple JSON response
    res = {}
    res['username'] = g.user.get_username()
    configs = []
    for c in g.user.get_api().get_configurations():
        configs.append({'id': c.get_id(), 'name': c.get_name()})
    res['configs'] = configs
    return jsonify(res)


#
# Example rest PUT call
#
@route(app, '/rest_example/put_test')
@util.rest_workflow_permission_required('rest_example')
@util.rest_exception_catcher
def rest_put_test():
    return jsonify({'result': request.get_json()['foo'] + ' plus some extra'})
