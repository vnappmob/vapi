"""app/api/v2/gold/doji.py"""
import datetime as dt
import os

import requests
from bson.decimal128 import Decimal128
from flask import Blueprint, current_app, jsonify, make_response, request

from app.api.auth import require_api_key
from app.api.v2.gold import bp
from app.api.v2.gold.get_query import get_query
from app.db.mongodb_connect import MongoDBConnect
from app.errors import error_response
from app.helper import PostFCM

SCOPE = 'gold'


@bp.route('/api/v2/gold/doji', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_gold_doji_get():
    """.. :quickref: 02. DOJI Price; Get DOJI Gold Price

    This function allows users to get the latest DOJI Gold price

    **Request**:

    .. sourcecode:: http

      GET /api/v2/gold/doji HTTP/1.1
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
                  "buy_hcm": 42550000.00,
                  "sell_hcm": 42550000.00
              }...
          ]
      }

    :query date_from: Set date from query
    :query date_to: Set date to query
    :reqheader Authorization: Bearer <api_key|scope=gold|permission=0>
    :resheader Content-Type: application/json
    :status 200: OK
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'gold_doji'
        date_from = request.args.get('date_from', default=0, type=int)
        date_to = request.args.get('date_to', default=0, type=int)

        if date_from != 0 and date_to != 0 and date_from < date_to:
            query = get_query(
                type=1,
                date_from=dt.datetime.fromtimestamp(date_from),
                date_to=dt.datetime.fromtimestamp(date_to)
            )
        else:
            query = get_query(type=0)

        q_res = db_connect.connection['vapi'][collection].aggregate(query)

        results = []
        for result in q_res:
            result.pop('_id', None)
            result['datetime'] = result['datetime'].strftime("%s")
            for k, v in result.items():
                if type(v) is Decimal128:
                    result[k] = Decimal128.to_decimal(v)

            results.append(result)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()


@bp.route('/api/v2/gold/doji', methods=['POST'])
@require_api_key(scope=SCOPE, permission=1)
def api_v2_gold_doji_post():
    """.. :quickref: 02. DOJI Price; Post DOJI Gold Price

    This function allows data manager to push newest data

    **Request**:

    .. sourcecode:: http

      POST /api/v2/gold/doji HTTP/1.1
      Host: https://vapi.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept

    :reqheader Authorization: Bearer <api_key|scope=gold|permission=1>
    :reqheader Content-Type: application/json
    :<json float buy_hcm: buy_hcm
    :<json float sell_hcm: sell_hcm
    :<json float buy_hn: buy_hn
    :<json float sell_hn: sell_hn
    :status 201: Successful
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'gold_doji'
        fcm = request.args.get('fcm', default=0, type=int)
        json_data = request.get_json()

        if fcm == 1:
            fcm_data = (
                '{"notification": {"title": "vPrice - Biến động giá DOJI"'
                ',"body": "HCM: Mua ' + '{:,d}'.format(
                    int(json_data['buy_hcm'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_hcm'])) +
                ' \nHN: Mua ' + '{:,d}'.format(
                    int(json_data['buy_hn'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_hn'])) +
                ' \nĐN: Mua ' + '{:,d}'.format(
                    int(json_data['buy_dn'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_dn'])) +
                ' \nCT: Mua ' + '{:,d}'.format(
                    int(json_data['buy_ct'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_ct'])) +
                ' ","sound": "default"},"priority": "high",'
                '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                '"id": "/topics/dojigold","status": "done"},'
                '"to": "/topics/dojigold"}'
            )

        sort = list({
            'datetime': -1
        }.items())
        last_row = db_connect.connection['vapi'][collection].find_one(
            sort=sort
        )
        changed = False

        for k, v in json_data.items():
            if type(v) is float:
                json_data[k] = Decimal128(str(v))

            if k not in last_row:
                changed = True
            elif (last_row[k]) != json_data[k]:
                changed = True

        if changed:
            json_data['datetime'] = dt.datetime.now()
            db_connect.connection['vapi'][collection].insert_one(json_data)

            if fcm == 1:
                fcm_response = PostFCM.post_fcm(fcm_data)
                print(fcm_response.status_code, fcm_response.text)

            return make_response((jsonify({'results': 201})), 201)
        return make_response((jsonify({'results': 200})), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
