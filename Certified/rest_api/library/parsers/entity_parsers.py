# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import reqparse

entity_parser = reqparse.RequestParser()
entity_parser.add_argument('name', location="json", help='The name of the entity.')
entity_parser.add_argument(
    'properties',
    location="json",
    help='The properties of the entity in the following format:key=value|key=value|',
)
