# Copyright 2020 BlueCat Networks. All rights reserved.

from main_app import api
from .entity_models import entity_model

configuration_model = api.clone(
    'configurations',
    entity_model
)
