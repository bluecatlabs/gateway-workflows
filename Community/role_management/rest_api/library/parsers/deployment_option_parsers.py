# Copyright 2023 BlueCat Networks. All rights reserved.

from flask_restx import reqparse

deployment_option_parser = reqparse.RequestParser()
deployment_option_parser.add_argument('collection', help="The name of the collection.",
                                      default='zones',
                                      choices=("blocks", "networks", "views", "zones"))
deployment_option_parser.add_argument('collection_name', help='The Name of the collection resource')
deployment_option_parser.add_argument('view', help='The Name of View', location='args')
deployment_option_parser.add_argument('server', help='Server use for filter', location='args')

create_deployment_option_parser = reqparse.RequestParser()
create_deployment_option_parser.add_argument('options', help='Options data of DNS Deployment Option', action='append',
                                             type=list,
                                             location='json')
create_deployment_option_parser.add_argument('collection', help="The name of the collection.", location='args',
                                             default='zones', choices=("blocks", "networks", "views", "zones"), )
create_deployment_option_parser.add_argument('collection_name', help='The Name of the collection resource',
                                             location='args')
create_deployment_option_parser.add_argument('view', help='The Name of View', location='args')

delete_deployment_option_parser = reqparse.RequestParser()
delete_deployment_option_parser.add_argument('ids', help='Ids of DNS Deployment Option', location='json',
                                             type=list)
