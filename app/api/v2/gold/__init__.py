""".. :quickref:
This module allows users to get gold data
"""
from flask import Blueprint

bp = Blueprint('api_v2_gold', __name__)

from app.api.v2.gold import sjc, doji, pnj  # This line must be after Blueprint

