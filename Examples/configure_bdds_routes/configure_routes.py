# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
from flask import request, url_for, redirect, render_template, jsonify, g, flash

from bluecat import route
from bluecat.api_exception import APIException
from main_app import app

# App configuration

# Get a list of configurations for display in a dropdown box.
def get_configurations():
    result = []
    if g.user:
        configs = g.user.get_api().get_configurations()
        for c in configs:
            result.append([c.get_id(), c.get_name()])
    return result
    
#
# Render the main new host page - allows the user to select a configuration and a block then enter a host name and IP address.
# If there isn't a logged in user, redirect to the home page.
#
@route(app, '/configure_bdds_routes/configure-routes')
def configure_routes():
    if g.user and g.user.has_page('configure_routes'):
        try:
            return render_template('configure-routes.html', configurations=get_configurations())
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

# Get a list of servers for a configuration
@route(app, '/configure_bdds_routes/list-servers/<configuration_id>')
def list_servers(configuration_id):
    if g.user and g.user.has_page('configure_routes'):
        try:
            c = g.user.get_api().get_entity_by_id(int(configuration_id))
            servers = {}
            for s in c.get_children_of_type('Server'):
                servers[s.get_id()] = s.get_name()
            return jsonify(servers)
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

# Get a list of static routes for a server
@route(app, '/configure_bdds_routes/list-static-routes/<server_id>')
def list_static_routes(server_id):
    if g.user and g.user.has_page('configure_routes'):
        try:
            return jsonify(g.user.get_api().get_entity_by_id(int(server_id)).get_static_routes())
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

# Update the static routes for a server
@route(app, '/configure_bdds_routes/update-static-routes/<server_id>', methods=['POST'])
def update_static_routes(server_id):
    if g.user and g.user.has_page('configure_routes'):
        try:
            g.user.get_api().get_entity_by_id(int(server_id)).update_static_routes(request.get_json())
            return jsonify({"result" : "success"})
        except APIException as e:
            return jsonify({"error" : e.get_message(), "result" : "failure"})
    else:
        return redirect(url_for('index'))
