"""app/api/v2/exchange_rate/ctg.py"""
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


@bp.route('/api/v2/exchange_rate/ctg', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_exchange_rate_ctg_get():
    """.. :quickref: 02. Vietinbank (CTG); Get all Vietinbank (CTG) exchange rate

    This function allows users to get the latest Vietinbank (CTG) exchange rate

    **Request**:

    .. sourcecode:: http

      GET /api/v2/exchange_rate/ctg HTTP/1.1
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
                  "buy_cash": 25416.27,
                  "buy_transfer": 25492.75,
                  "sell": 26258.39
              },
              {
                  "currency": "USD",
                  "buy_cash": 23130.00,
                  "buy_transfer": 23130.00,
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
        collection = 'exchange_rate_ctg'

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


@bp.route('/api/v2/exchange_rate/ctg', methods=['POST'])
@require_api_key(scope=SCOPE, permission=1)
def api_v2_exchange_rate_ctg_post():
    """.. :quickref: 02. Vietinbank (CTG); Post new exchange rate

    This function allows data manager to push newest data

    **Request**:

    .. sourcecode:: http

      POST /api/v2/exchange_rate/ctg HTTP/1.1
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
    :<json float buy_cash: buy_cash
    :<json float buy_transfer: buy_transfer
    :<json float sell: sell
    :status 201: Successful
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'exchange_rate_ctg'
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
                        '{"notification": {"title": "vPrice - Biến động tỷ giá Vietinbank (CTG)-%s",'
                        '"body": "Mua tiền mặt: %s'
                        '\nMua chuyển khoản: %s'
                        '\nBán: %s","sound": "default"},"priority": "high",'
                        '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                        '"id": "/topics/exchange_rate.ctg.%s","status": "done"},'
                        '"to": "/topics/exchange_rate.ctg.%s"}' %
                        (
                            new_doc['currency'],
                            '{:,.2f}'.format(new_doc['buy_cash']),
                            '{:,.2f}'.format(new_doc['buy_transfer']),
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
