# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
from flask import render_template
from flask import jsonify
from flask import g

from bluecat import route
from bluecat import util
from bluecat.api_exception import APIException
from main_app import app


# Get a list of configurations for display in a dropdown box.
def get_configurations():
    result = []
    if g.user:
        configs = g.user.get_api().get_configurations()
        for c in configs:
            result.append([c.get_id(), c.get_name()])
    return result


# WORKFLOW ENTRYPOINT
# The workflow name must be the first part of any endpoints defined in this file. 
# If the route path doesn't share this convention collision with other workflow
# endpoints might occur. As best practive preface the route with the name of the
# workflow to avoid conflicts
# This endpoint renders the page template and displays it to the user
@route(app, '/create_block/block_page')
@util.workflow_permission_required('create_block_page')
@util.exception_catcher
def create_block_create_block_page():
    g.user.logger.info('User entered workflow page')
    return render_template('create_block_page.html', configurations=get_configurations())


# Endpoint for creating a block with the parameters are passed through a URL.
# This endpoint is called by the associated JavaScript that is triggered on
# the "onClick" event of the button defined in the HTML
@route(app, '/create_block/block_page/<parent_id>/<blockname>/<cidr>/<mask>')
@util.workflow_permission_required('create_block_page')
@util.exception_catcher
def create_block(parent_id, blockname, cidr, mask):
    logstring = 'create_block called with parent_id: %s, blockname: %s, cidr: %s, mask %s' % (
        parent_id,
        blockname,
        cidr,
        mask
    )
    g.user.logger.info(util.safe_str(logstring))
    # Fetch the parent object of the block
    result = {}
    parent = g.user.get_api().get_entity_by_id(int(parent_id))

    # Attempt to create an IP4Block with the provided paramters. Result is parsed in the JS
    # And displays the error message
    try:
        ipv4_block = parent.add_ip4_block_by_cidr(cidr + "/" + mask, ["name=" + blockname])
        ipv4_block.get_deployment_roles()
        g.user.logger.info('Created IP4Block, id: %s' % (ipv4_block.get_id()))
    except APIException as error:
        result['result'] = error.get_message()
        logstring = 'ERROR: %s' % (error.get_message())
        g.user.logger.info(logstring)
        return jsonify(result)

    # Ensure that the block was created by retrieving the created object from the BAM Again
    # This is a validation step only.
    if int(ipv4_block.get_parent().get_id()) == int(parent_id):
        result['result'] = 'succeed'
        result['parent_id'] = ipv4_block.get_parent().get_id()
        g.user.logger.info('Block creation confirmed')
    else:
        result['result'] = 'fail'
        g.user.logger.info('ERROR: Unable to retrieve entity from BAM')

    # Return the result dictionary for parsing in the JS Script
    return jsonify(result)


@route(app, '/create_block/search_block_child/<parent_id>')
@util.workflow_permission_required('create_block_page')
@util.exception_catcher
def search_block(parent_id):
    blocks = {}
    parent = g.user.get_api().get_entity_by_id(int(parent_id))
    block_list = parent.get_ip4_blocks()
    for block in block_list:
        blocks[block.get_id()] = [block.get_name(), block.get_properties()['CIDR']]
    return jsonify(blocks)
