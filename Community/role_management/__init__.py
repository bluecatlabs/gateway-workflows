# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
from flask import Blueprint
from flask_restx import Api
from main_app import app

from bluecat.gateway.logging import spawn_logger_adapter

api_endpoints = Blueprint("rm_api", "rm")
bp_rm = Api(api_endpoints)
app.register_blueprint(api_endpoints, url_prefix="/role-management/v1")
logger = spawn_logger_adapter("RoleManagement")
