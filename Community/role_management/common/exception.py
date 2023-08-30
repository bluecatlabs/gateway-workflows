# Copyright 2023 BlueCat Networks. All rights reserved.
from bluecat.api_exception import safe_str


class UserException(Exception):
    def __init__(self, msg):
        self.msg = msg or "User input incorrect"

    def __str__(self):
        return safe_str(self.msg)


class InvalidParam(UserException):
    def __init__(self, mess=''):
        message = mess or 'Invalid input'
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return safe_str(self.message)


class RESTv2ResponseException(UserException):
    """UserException"""


class BAMAuthException(UserException):
    def __init__(self, msg=''):
        self.msg = msg or "Session expired"

    def __str__(self):
        return safe_str(self.msg)


class NotSupportedRestV2(Exception):
    def __init__(self, version):
        self.msg = 'BAM version {} not supported REST APIv2.'.format(version)

    def __str__(self):
        return safe_str(self.msg)


class MissingConfigFile(UserException):
    def __init__(self, file_name):
        message = 'Missing or invalid config in {} file'.format(file_name)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return safe_str(self.message)


###
# Migration XML Exception
###

class HeaderMissingException(Exception):
    def __init__(self, header):
        self.msg = "Header '{}' is missing.".format(header)

    def __str__(self):
        return self.msg


class InvalidDNSOptionException(Exception):
    def __init__(self, mess=''):
        message = mess or 'Invalid DNS Options'
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return safe_str(self.message)


###
# Action Exception
###
class ActionConflictException(UserException):
    def __init__(self, msg=''):
        self.msg = msg or "Action is conflicted"

    def __str__(self):
        return self.msg


class InvalidZoneTransferInterfaceException(UserException):
    def __init__(self, msg=''):
        self.msg = msg or "Invalid Zone Transfer Server Interface"

    def __str__(self):
        return self.msg
