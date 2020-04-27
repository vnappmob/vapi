"""app/api/v2/exchange_rate/sbv.py"""
import datetime
from collections import defaultdict

import requests
from bson.decimal128 import Decimal128
from flask import Blueprint, current_app, jsonify, make_response, request

from app.api.auth import require_api_key
from app.api.v2.exchange_rate import bp
from app.db.mongodb_connect import MongoDBConnect
from app.errors import error_response
from app.helper import PostFCM

SCOPE = 'exchange_rate'


@bp.route('/api/v2/exchange_rate/sbv', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_exchange_rate_sbv_get():
    """.. :quickref: SBV; Get all SBV exchange rate

    This function allows users to get the latest Ngân Hàng Nhà Nước (SBV) exchange rate

    **Request**:

    .. sourcecode:: http

      GET /api/v2/exchange_rate/sbv HTTP/1.1
      Host: https://vapi.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
          "results": [
              {
                  "currency": "EUR",
                  "buy": 25416.27,
                  "sell": 26258.39
              },
              {
                  "currency": "USD",
                  "buy": 23130.00,
                  "sell": 23250.00
              }...
          ]
      }

    :reqheader Authorization: Bearer <api_key|scope=exchange_rate|permission=0>
    :resheader Content-Type: application/json
    :status 200: OK
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'exchange_rate_sbv'

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
                    'buy': {
                        '$first': '$buy'
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
                    'buy': {
                        '$toDouble': '$buy'
                    }
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


@bp.route('/api/v2/exchange_rate/sbv', methods=['POST'])
@require_api_key(scope=SCOPE, permission=1)
def api_v2_exchange_rate_sbv_post():
    """.. :quickref: SBV; Post new exchange rate

    This function allows data manager to push newest data

    **Request**:

    .. sourcecode:: http

      POST /api/v2/exchange_rate/sbv HTTP/1.1
      Host: https://vapi.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept

    :reqheader Authorization: Bearer <api_key|scope=exchange_rate|permission=1>
    :reqheader Content-Type: application/json
    :<json List[json] post_datas: List of json data with below params
    :<json string currency: currency code (3 chars: VND, USD...)
    :<json float buy: buy
    :<json float sell: sell
    :status 201: Successful
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'exchange_rate_sbv'
        fcm = request.args.get('fcm', default=0, type=int)
        json_data = request.get_json()

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
                    'buy': {
                        '$first': '$buy'
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
                    'buy': {
                        '$toDouble': '$buy'
                    }
                }
            }
        ])

        post_dict = {}
        for data in json_data['post_datas']:
            post_dict[data.pop('currency')] = data

        current_dict = {}
        for data in q_res:
            current_dict[data.pop('currency')] = data

        changed = False

        for k, v in post_dict.items():
            if k not in current_dict or post_dict[k] != current_dict[k]:
                changed = True
                new_doc = {
                    "datetime": datetime.datetime.now(),
                    "currency": k
                }
                new_doc.update(v)
                db_connect.connection['vapi'][collection].insert_one(new_doc)
                if fcm == 1:
                    fcm_data = (
                        '{"notification": {"title": "vPrice - Biến động tỷ giá Ngân Hàng Nhà Nước (SBV)-%s",'
                        '"body": "Mua: %s\nBán: %s","sound": "default"},"priority": "high",'
                        '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                        '"id": "/topics/exchange_rate/sbv/%s","status": "done"},'
                        '"to": "/topics/exchange_rate/sbv/%s"}' %
                        (
                            new_doc['currency'],
                            '{:,.2f}'.format(new_doc['buy']),
                            '{:,.2f}'.format(new_doc['sell']),
                            new_doc['currency'],
                            new_doc['currency']
                        )
                    )

                    fcm_response = PostFCM.post_fcm(fcm_data)
                    print(fcm_response.status_code, fcm_response.text)

        if changed:
            return make_response((jsonify({'results': 201})), 201)
        return make_response((jsonify({'results': 200})), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
