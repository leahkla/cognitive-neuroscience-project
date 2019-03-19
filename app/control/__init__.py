"""
This file creates a blueprint for the control functionalities.
"""

from flask import Blueprint

bp = Blueprint('control', __name__)

from app.control import routes