import os

from flask import send_from_directory, request, g

from bluecat import route
from bluecat.gateway.decorators import api_exc_handler, require_permission, page_exc_handler
from bluecat.gateway.errors import BadRequestError, FieldError
from bluecat.util import no_cache
from main_app import app


@route(app, "/role_management_ui/page")
@page_exc_handler(default_message="Failed to load role_management workflow.")
@require_permission("role_management")
def role_management():
    return send_from_directory(
        os.path.dirname(os.path.abspath(str(__file__))), "roleMntPage/index.html"
    )

