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


@route(app, '/device_management/device_management_endpoint')
@util.workflow_permission_required('device_management_page')
@util.exception_catcher
@util.ui_secure_endpoint
def device_management_device_management_page():
    return render_template(
        'device_management_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )
