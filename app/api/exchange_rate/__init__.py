"""app/api/exchange_rate.py"""
import requests
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_exchange_rate', __name__)  # pylint: disable=C

from app.api.exchange_rate import sbv, vcb  # This line must be after Blueprint
