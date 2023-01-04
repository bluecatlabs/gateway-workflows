# Copyright 2022 BlueCat Networks. All rights reserved.
from flask_restplus import reqparse

encrypt_credential_parser = reqparse.RequestParser()
encrypt_credential_parser.add_argument('username', location="json", required=True, help='The username of the account')
encrypt_credential_parser.add_argument('password', location="json", required=True, help='The password to be encrypted')
