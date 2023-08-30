# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
from flask_restx import reqparse

hint_parser = reqparse.RequestParser()

hint_parser.add_argument('limit', default=10, type=int, location='args',
                         help='Limit number of the response records')
hint_parser.add_argument('hint', default='', type=str, location='args',
                         help='Hint for filtering the records')

zone_by_hint_parser = reqparse.RequestParser()
zone_by_hint_parser.add_argument('limit', default=10, type=int, location='args',
                                 help='Limit number of the response records')
zone_by_hint_parser.add_argument('hint', default='', type=str, location='args',
                                 help='Hint for filtering the records')
zone_by_hint_parser.add_argument('view_name', default='', type=str, location='args',
                                 help='View name contains zones')
