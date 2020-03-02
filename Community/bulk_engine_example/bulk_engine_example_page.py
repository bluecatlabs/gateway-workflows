# Copyright 2019 BlueCat Networks. All rights reserved.

import os
from flask import url_for, redirect, render_template, g
from bluecat_portal.customizations.bulk_engine.loader import load
from bluecat import route, util
import config.default_config as config
from main_app import app
from .bulk_engine_example_form import GenericFormTemplate
import json
def module_path():
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/bulk_engine_example/bulk_example')
@util.workflow_permission_required('bulk_engine_example_page')
@util.exception_catcher
def bulk_engine_example_bulk_engine_example_page():
    form = GenericFormTemplate()
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'bulk_engine_example_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/bulk_engine_example/form', methods=['POST'])
@util.workflow_permission_required('bulk_engine_example_page')
@util.exception_catcher
def bulk_engine_example_bulk_engine_example_page_form():
    form = GenericFormTemplate()
    form.configuration.choices = util.get_configurations(default_val=True)
    data = json.loads(form.data_box.data)
    name = g.user.get_api().get_entity_by_id(form.configuration.data).get_name()
    view = form.view.data
    globals = {
        "configuration": name,
        "view": view,
        "on_fail": form.on_fail.data
    }
    r = load(data, **globals)

    response = ""
    for type, result in r.items():
        response += "<h2>%s</2>" % type
        response += "<pre>%s</pre>" % str(result).replace(',', ',\n')


    form.results.plain_html = response

    return render_template(
        'bulk_engine_example_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )
