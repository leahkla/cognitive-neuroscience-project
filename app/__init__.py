"""
This  file initiates the flask app.
"""

from flask import Flask
from app.config import Config

# Initiate the flask app:
app = Flask(__name__)

# Load app configuration from the Config object:
app.config.from_object(Config)

# Load the routes:
from app import routes
