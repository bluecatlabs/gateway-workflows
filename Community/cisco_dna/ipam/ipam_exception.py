from bluecat.api_exception import RESTException

class BadRequest(RESTException):
	def __init__(self, message):
		super(BadRequest, self).__init__(message)


class IpPoolBadRequestException(RESTException):
	def __init__(self, message):
		super(IpPoolBadRequestException, self).__init__(message)


class IpPoolAlreadyExistsException(RESTException):
	def __init__(self, message):
		super(IpPoolAlreadyExistsException, self).__init__(message)


class IpPoolInUseException(RESTException):
	def __init__(self, message):
		super(IpPoolInUseException, self).__init__(message)

		
class IpSubpoolNotEmptyException(RESTException):
	def __init__(self, message):
		super(IpSubpoolNotEmptyException, self).__init__(message)


class IpSubpoolAlreadyExistsException(RESTException):
	def __init__(self, message):
		super(IpSubpoolAlreadyExistsException, self).__init__(message)


class IpAddressNotAvailableException(RESTException):
	def __init__(self, message):
		super(IpAddressNotAvailableException, self).__init__(message)