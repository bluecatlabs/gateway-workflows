import os
from time import gmtime, strftime

from flask import g
from werkzeug.utils import secure_filename


def safe_open(path):
    """
    Creates path if it does not exist
    :param path: path to check if exists else create
    :return: opened path object
    """
    if not os.path.exists(path):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
    return open(path, 'w')


def generate_filename(filename):
    """
    Generate a secure filename given a base filename - appends current time and username
    :param filename: base filename
    :return: secure filename
    """
    username = g.user.get_username()
    return secure_filename(str(strftime("%H:%M:%S", gmtime())) + '-' + username + '-' + filename)
