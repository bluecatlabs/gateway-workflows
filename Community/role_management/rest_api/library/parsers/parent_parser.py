# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
from flask_restx import reqparse

parent_parser = reqparse.RequestParser()

parent_parser.add_argument('collections', default="servers", type=str, location='args', required=True,
                            help='The name of the collection. Available values : configurations, views, zones, servers, blocks',
                            choices=("configurations", "views", "zones", "servers", "blocks"))

