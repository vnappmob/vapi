""".. :quickref:
This module allows users to get exchange rate data
"""
from flask import Blueprint

bp = Blueprint('api_v2_exchange_rate', __name__)

from app.api.v2.exchange_rate import vcb, ctg, tcb, bid  # This line must be after Blueprint
