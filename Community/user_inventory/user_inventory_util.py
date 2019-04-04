from flask import make_response, jsonify

http_code_map = {
    200: 'Ok',
    400: 'Bad Request',
    500: 'Internal Server Error'
}


def response_handler(description, http_code):
    """
    :param description: Description of response
    :param http_code: HTTP error code
    :return: JSON response to REST endpoint with a status, code and description
    """
    return make_response(jsonify({
        'status': http_code_map[http_code],
        'code': http_code,
        'description': description
    }), http_code)
