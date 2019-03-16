"""
This file specifies how the flask app is configured.
"""

import os


class Config(object):
    """
    The configuration parameters for the flask app.
    """
    SESSION_TYPE = 'memcached'
    # If there is an environment variable set with a secret key, use it:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secret_key'
