# Copyright 2018 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
from flask import url_for, redirect, render_template, flash, g
from bluecat import route, util
import config.default_config as config
from main_app import app
from .network_manager_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(str(__file__, encoding)))


@route(app, '/network_manager/network_manager_endpoint')
@util.workflow_permission_required('network_manager_page')
@util.exception_catcher
def network_manager_network_manager_page():
    form = GenericFormTemplate()
    u = g.user.get_api().get_user(g.user.get_username())
    groups = u.get_user_groups()
    has_block = False
    for group in groups:
        bv = g.user.get_api().get_by_object_types(group.name, ['IP4Block'])
        has_block=False
        for b in bv:
            has_block = True
            break
    if has_block == False:
        flash("You don't have any network space allocated to your group")
    return render_template(
        'network_manager_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/network_manager/form', methods=['POST'])
@util.workflow_permission_required('network_manager_page')
@util.exception_catcher
def network_manager_network_manager_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():
        block = None
        u = g.user.get_api().get_user(g.user.get_username())
        groups = u.get_user_groups()
        for group in groups:
            bv = g.user.get_api().get_by_object_types(group.name, ['IP4Block'])
            for b in bv:
                block = b
                break
        if block is None:
            flash("This doesn't work, you has no block.")
            app.logger.error("This doesn't work, you has no block.")
            return render_template(
                'network_manager_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )
        n = block.get_next_available_ip_range(form.network_size.data, "IP4Network")
        n.name = "%s | %s" % (form.network_location.data, form.network_name.data)
        n.update()

        g.user.logger.info('SUCCESS')
        flash('Created network %s with %s addresses at %s'%(n.name, form.network_size.data, n.get_property("CIDR")), 'succeed')
        return redirect(url_for('network_managernetwork_manager_network_manager_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'network_manager_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
