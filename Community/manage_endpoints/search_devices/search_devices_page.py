# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
from flask import render_template, g
from bluecat import route, util
import config.default_config as config
from main_app import app


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/search_devices/search_devices_endpoint')
@util.workflow_permission_required('search_devices_page')
@util.exception_catcher
@util.ui_secure_endpoint
def search_devices_search_devices_page():
    return render_template(
        'search_devices_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )
