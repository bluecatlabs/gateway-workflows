from bluecat.api_exception import safe_str


class UserException(Exception):
    def __init__(self, msg):
        self.msg = msg or "User input incorrect"

    def __str__(self):
        return safe_str(self.msg)


class NetworkNotFound(UserException):
    def __init__(self, network_cidr):
        self.network_cidr = network_cidr
        message = 'Not found network {}'.format(network_cidr)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return safe_str(self.message)
