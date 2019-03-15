"""
This  file initiates the flask app.
"""

from flask import Flask
from app.config import Config

app = Flask(__name__)

# Load configuration from the Config object:
app.config.from_object(Config)

from app import routes
