from flask_restplus import fields

from main_app import api

encrypt_credential_model = api.clone(
    'encrypt_credential',
    {
        'username': fields.String(required=True, description='The username of the account'),
        'password': fields.String(required=True, description='The password to be encrypted')
    }
)
