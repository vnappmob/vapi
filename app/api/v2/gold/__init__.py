""".. :quickref:
This module allows users to get gold data
"""
import requests
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.mongodb_connect import MongoDBConnect
from app.errors import error_response
from app.api.auth import require_api_key
from app.helper import PostFCM
import os
from bson.decimal128 import Decimal128
import datetime

bp = Blueprint('api_v2_gold', __name__)  # pylint: disable=C

SCOPE = 'gold'


@bp.route('/api/v2/gold/sjc', methods=['GET'])
@require_api_key(scope=SCOPE, permission=0)
def api_v2_gold_sjc_get():
    """.. :quickref: 01. SJC Price; Get SJC Gold Price

    This function allows users to get the latest SJC Gold price

    **Request**:

    .. sourcecode:: http

      GET /api/v2/gold/sjc HTTP/1.1
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
                  "buy_1l": 42550000.00,
                  "sell_1l": 42550000.00,
                  ...
              }
          ]
      }

    :query date_from: Set date from query
    :query date_to: Set date to query
    :reqheader Authorization: Bearer <api_key|scope=gold|permission=1>
    :resheader Content-Type: application/json
    :status 200: OK
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'gold_sjc'
        date_from = request.args.get('date_from', default=0, type=int)
        date_to = request.args.get('date_to', default=0, type=int)

        filter = {}
        sort = list({
            'datetime': -1
        }.items())
        limit = 1

        q_res = db_connect.connection['vapi'][collection].find(
            filter=filter,
            sort=sort,
            skip=0,
            limit=limit
        )

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


@bp.route('/api/v2/gold/sjc', methods=['POST'])
@require_api_key(scope=SCOPE, permission=1)
def api_v2_gold_sjc_post():
    """.. :quickref: 01. SJC Price; Post SJC Gold Price

    This function allows data manager to push newest data

    **Request**:

    .. sourcecode:: http

      POST /api/v2/gold/sjc HTTP/1.1
      Host: https://vapi.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept

    :reqheader Authorization: Bearer <api_key|scope=gold|permission=2>
    :reqheader Content-Type: application/json
    :<json float buy_1l: buy_1l
    :<json float sell_1l: sell_1l
    :<json float buy_1c: buy_1c
    :<json float sell_1c: sell_1c
    :<json float buy_nhan1c: buy_nhan1c
    :<json float sell_nhan1c: sell_nhan1c
    :<json float buy_trangsuc49: buy_trangsuc49
    :<json float sell_trangsuc49: sell_trangsuc49
    :status 201: Successful
    :status 400: Error
    :status 403: Fail on authorization
    """
    try:
        db_connect = MongoDBConnect()
        collection = 'gold_sjc'
        fcm = request.args.get('fcm', default=False, type=bool)
        json_data = request.get_json()

        if fcm:
            fcm_data = (
                '{"notification": {"title": "vPrice - Biến động giá SJC"'
                ',"body": "1L: Mua ' + '{:,d}'.format(
                    int(json_data['buy_1l'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_1l'])) +
                '\n1c: Mua ' + '{:,d}'.format(
                    int(json_data['buy_1c'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_1c'])) +
                '\nTrang sức: Mua ' + '{:,d}'.format(
                    int(json_data['buy_trangsuc49'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_trangsuc49'])) +
                ' ","sound": "default"},"priority": "high",'
                '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                '"id": "/topics/sjcgold","status": "done"},'
                '"to": "/topics/sjcgold"}'
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
            json_data['datetime'] = datetime.datetime.utcnow()
            db_connect.connection['vapi'][collection].insert_one(json_data)

            if fcm:
                fcm_response = PostFCM(fcm_data)
                print(fcm_response)

            return make_response((jsonify({'results': 201})), 201)
        return make_response((jsonify({'results': 200})), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()


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
              }
          ]
      }

    :query date_from: Set date from query
    :query date_to: Set date to query
    :reqheader Authorization: Bearer <api_key|scope=gold|permission=1>
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

        filter = {}
        sort = list({
            'datetime': -1
        }.items())
        limit = 1

        q_res = db_connect.connection['vapi'][collection].find(
            filter=filter,
            sort=sort,
            skip=0,
            limit=limit
        )

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

    :reqheader Authorization: Bearer <api_key|scope=gold|permission=2>
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
        fcm = request.args.get('fcm', default=False, type=bool)
        json_data = request.get_json()

        if fcm:
            fcm_data = (
                '{"notification": {"title": "vPrice - Biến động giá DOJI"'
                ',"body": "HCM: Mua ' + '{:,d}'.format(
                    int(json_data['buy_hcm'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_hcm'])) +
                ' \nHN: Mua ' + '{:,d}'.format(
                    int(json_data['buy_hn'])) + ' - Bán ' +
                '{:,d}'.format(int(json_data['sell_hn'])) +
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
            json_data['datetime'] = datetime.datetime.utcnow()
            db_connect.connection['vapi'][collection].insert_one(json_data)

            if fcm:
                fcm_response = PostFCM(fcm_data)
                print(fcm_response)

            return make_response((jsonify({'results': 201})), 201)
        return make_response((jsonify({'results': 200})), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()