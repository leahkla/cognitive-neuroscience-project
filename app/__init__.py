"""
This  file initiates the flask app.
"""

from flask import Flask
from app.config import Config
# from flask.ext.session import Session
from flask_session.__init__ import Session

# SESSION_TYPE = 'redis'
# app.config.from_object(__name__)
app = Flask(__name__)
app.config.from_object(Config)

sess = Session()

from app import routes
