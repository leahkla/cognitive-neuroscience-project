"""
This file creates a blueprint for the researcher interface.
"""

from flask import Blueprint

bp = Blueprint('researcher', __name__)

from app.researcher import routes