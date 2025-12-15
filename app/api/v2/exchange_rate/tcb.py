"""app/api/v2/exchange_rate/tcb.py"""
import datetime
from collections import defaultdict

import requests
from bson.decimal128 import Decimal128
from flask import Blueprint, current_app, jsonify, make_response, request

from app.api.auth import require_api_key
from app.api.v2.exchange_rate import bp
from app.db.mongodb_connect import MongoDBConnect
from app.errors import error_response

SCOPE = 'exchange_rate'


@bp.route('/api/v2/exchange_rate/tcb', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_exchange_rate_tcb_get():
    """.. :quickref: 03. Techcombank (TCB); Get all Techcombank (TCB) exchange rate

    This function allows users to get the latest Techcombank (TCB) exchange rate.
    Optionally, you can specify a date and/or currency to filter the results.

    **Request**:

    .. sourcecode:: http

      GET /api/v2/exchange_rate/tcb HTTP/1.1
      Host: https://api.vnappmob.com
      Accept: application/json

      GET /api/v2/exchange_rate/tcb?date=2024-01-15 HTTP/1.1
      Host: https://api.vnappmob.com
      Accept: application/json

      GET /api/v2/exchange_rate/tcb?currency=USD HTTP/1.1
      Host: https://api.vnappmob.com
      Accept: application/json

      GET /api/v2/exchange_rate/tcb?date=2024-01-15&currency=USD HTTP/1.1
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
    :queryparam date: Optional date parameter in YYYY-MM-DD format to filter results by specific date
    :queryparam currency: Optional currency code (3 chars: USD, EUR, etc.) to filter results by specific currency
    :resheader Content-Type: application/json
    :status 200: OK
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'exchange_rate_tcb'

        # Build aggregation pipeline
        pipeline = []

        # Build match filter conditions
        match_conditions = {}

        # Add date filter if date parameter is provided
        date_param = request.args.get('date')
        if date_param:
            try:
                # Parse the date string (YYYY-MM-DD format)
                query_date = datetime.datetime.strptime(date_param, '%Y-%m-%d')
                # Create date range: start of day to end of day
                start_of_day = query_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = query_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                match_conditions['datetime'] = {
                    '$gte': start_of_day,
                    '$lte': end_of_day
                }
            except ValueError:
                return error_response(400, 'Invalid date format. Use YYYY-MM-DD format.')

        # Add currency filter if currency parameter is provided
        currency_param = request.args.get('currency')
        if currency_param:
            match_conditions['currency'] = currency_param.upper()

        # Add match stage if any filters are provided
        if match_conditions:
            pipeline.append({
                '$match': match_conditions
            })

        # Add sorting, grouping, and projection stages
        pipeline.extend([
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

        q_res = db_connect.connection['vapi'][collection].aggregate(pipeline)

        results = list(q_res)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()


@bp.route('/api/v2/exchange_rate/tcb', methods=['POST'])
@require_api_key(scope=SCOPE, permission=1)
def api_v2_exchange_rate_tcb_post():
    """.. :quickref: 03. Techcombank (TCB); Post new exchange rate

    This function allows data manager to push newest data

    **Request**:

    .. sourcecode:: http

      POST /api/v2/exchange_rate/tcb HTTP/1.1
      Host: https://api.vnappmob.com
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
        collection = 'exchange_rate_tcb'
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

        if changed:
            return make_response((jsonify({'results': 201})), 201)
        return make_response((jsonify({'results': 200})), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
