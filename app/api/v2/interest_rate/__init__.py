""".. :quickref:
This module allows users to get/post interest rate data
"""
from app.helper import PostFCM
from app.errors import error_response
from app.db.mongodb_connect import MongoDBConnect
from app.api.auth import require_api_key
from flask import Blueprint, current_app, jsonify, make_response, request
from bson.decimal128 import Decimal128
import requests
from collections import defaultdict
import datetime
from flask import Blueprint

bp = Blueprint('api_v2_interest_rate', __name__)

SCOPE = 'interest_rate'


@bp.route('/api/v2/interest_rate/<string:bankcode>', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_interest_rate_get(bankcode):
    """.. :quickref: 01. Interest Rate; Get interest rate by BankCode

    This function allows users to get the latest interest rate

    **Request**:

    .. sourcecode:: http

      GET /api/v2/interest_rate/{bankcode} HTTP/1.1
      Host: https://api.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
          "results": [
              {
                  "period": "1 tháng",
                  "rate": 4.10
              },
              {
                  "period": "2 tháng",
                  "rate": 4.10
              }...
          ]
      }

    :reqheader Authorization: Bearer <api_key|scope=interest_rate|permission=0>
    :resheader Content-Type: application/json
    :status 200: OK
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = SCOPE + '_' + bankcode

        q_res = db_connect.connection['vapi'][collection].aggregate([
            {
                '$sort': {
                    'datetime': -1
                }
            }, {
                '$group': {
                    '_id': '$currency',
                    'datetime': {
                        '$first': '$datetime'
                    },
                    'sell': {
                        '$first': '$sell'
                    },
                    'buy_cash': {
                        '$first': '$buy_cash'
                    },
                    'buy_transfer': {
                        '$first': '$buy_transfer'
                    }
                }
            }, {
                '$sort': {
                    '_id': 1
                }
            }, {
                '$project': {
                    '_id': False,
                    'currency': '$_id',
                    'sell': {
                        '$toDouble': '$sell'
                    },
                    'buy_cash': {
                        '$toDouble': '$buy_cash'
                    },
                    'buy_transfer': {
                        '$toDouble': '$buy_transfer'
                    },
                }
            }
        ])

        results = list(q_res)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
