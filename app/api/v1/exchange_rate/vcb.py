"""app/api/exchange_rate/vcb.py"""
from collections import defaultdict
import requests
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response
from app.api.v1.exchange_rate import bp


@bp.route('/api/exchange_rate/vcb', methods=['GET'])
def api_exchange_rate_vcb_get():
    """.. :quickref: 01. VCB; Get all VCB exchange rate

    This function allows users to get the latest VCB exchange rate

    **Request**:

    .. sourcecode:: http

      GET /api/exchange_rate/vcb HTTP/1.1
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
              }
          ]
      }

    :query api_key: API Key generated by VNAppMob
    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.args.get('api_key', default='', type=str)

            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:
                statements = (
                    'SELECT t1.currency, t1.buy_cash, t1.buy_transfer, t1.sell '
                    'FROM vnappmob_exchange_rate_vcb t1 '
                    'WHERE id IN ( '
                    'SELECT MAX(id) FROM vnappmob_exchange_rate_vcb '
                    'GROUP BY currency '
                    ') ORDER BY t1.currency ASC')
                try:
                    results = db_connect.readall(statements)
                    return make_response((jsonify({'results': results})), 200)
                except MySQLdb.Error as err:  # pylint: disable=E
                    return error_response(400, str(err))
            return error_response(403, 'Invalid api_key')
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/exchange_rate/vcb', methods=['POST'])
def api_exchange_rate_vcb_post():
    """.. :quickref: 01. VCB; Post new exchange rate

    Limited function that allows data manager to push newest price

    **Request**:

    .. sourcecode:: http

      POST /api/exchange_rate/vcb HTTP/1.1
      Host: https://vapi.vnappmob.com
      Accept: application/json

    **Response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept

    :reqheader Authorization: API Key generated by VNAppMob
    :reqheader Content-Type: application/json
    :<json List[json] post_datas: List of json data with below params
    :<json string currency: currency code (3 chars: VND, USD...)
    :<json float buy_cash: buy_cash
    :<json float buy_transfer: buy_transfer
    :<json float sell: sell
    :status 201: Successful update data
    :status 403: Invalid api_key
    :status 400: Error
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.headers['Authorization']
            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:

                latest_datas = db_connect.readall(
                    'SELECT t1.currency, t1.buy_cash, t1.buy_transfer, t1.sell '
                    'FROM vnappmob_exchange_rate_vcb t1 '
                    'WHERE id IN ( '
                    'SELECT MAX(id) FROM vnappmob_exchange_rate_vcb '
                    'GROUP BY currency '
                    ') ORDER BY t1.currency ASC')

                latest_datas_dict = defaultdict(list)
                for data in latest_datas:
                    latest_datas_dict[data['currency']] = data

                json_data = request.get_json()
                post_datas = json_data['post_datas']
                changed_list = []
                for post_data in post_datas:
                    currency = post_data['currency']
                    buy_cash = post_data['buy_cash']
                    buy_transfer = post_data['buy_transfer']
                    sell = post_data['sell']
                    latest_data = latest_datas_dict[currency]

                    if latest_data:
                        if any([
                                float(latest_data['buy_cash']) !=
                                float(buy_cash),
                                float(latest_data['buy_transfer']) !=
                                float(buy_transfer),
                                float(latest_data['sell']) != float(sell),
                        ]):
                            changed_list.append(currency)
                            insert_new_data(db_connect, currency, buy_cash,
                                            buy_transfer, sell)
                    else:
                        changed_list.append(currency)
                        insert_new_data(db_connect, currency, buy_cash,
                                        buy_transfer, sell)

                if changed_list:
                    print(changed_list)
                    return make_response((jsonify({'results': 201})), 201)
                return make_response((jsonify({'results': 200})), 200)
            return error_response(403, 'Invalid api_key')
        except MySQLdb.Error as err:  # pylint: disable=E
            print(err)
            return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


def insert_new_data(db_connect, currency, buy_cash, buy_transfer, sell):
    """insert_new_data"""
    vals = []
    statements = ("INSERT INTO vnappmob_exchange_rate_vcb "
                  "(id, currency, buy_cash, buy_transfer, sell) "
                  "VALUES (NULL, %s, %s, %s, %s);")
    vals.extend((currency, buy_cash, buy_transfer, sell))
    db_connect.writecommit(statements, tuple(vals))


def push_fcm():
    """Trigger push to FCM"""
    ###TODO: Review these lines before trigger to FCM
    # headers = {
    #     'Authorization':
    #     'key=' + current_app.config['VPRICE_FCM_KEY'],
    #     'Content-Type':
    #     'application/json'
    # }
    #
    # push_data_currency = json_data['currency']
    # push_data_buy_cash = '{:,d}'.format(
    #     int(json_data['buy_cash']))
    # push_data_buy_transfer = '{:,d}'.format(
    #     int(json_data['buy_transfer']))
    # push_data_sell = '{:,d}'.format(int(json_data['sell']))
    # data = (
    #     '{"notification": {"title": "vPrice - Biến động giá VCB-%s,'
    #     '"body": "Mua tiền mặt: %s'
    #     '\nMua chuyển khoản: %s'
    #     '\nBán: %s","sound": "default"},"priority": "high",'
    #     '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
    #     '"id": "/topics/exchange_rate/vcb/%s","status": "done"},'
    #     '"to": "/topics/exchange_rate/vcb/%s"}' %
    #     (push_data_currency, push_data_buy_cash,
    #      push_data_buy_transfer, push_data_sell,
    #      push_data_currency, push_data_currency))
    #
    # response = requests.post(
    #     'https://fcm.googleapis.com/fcm/send',
    #     headers=headers,
    #     data=data.encode('utf-8'))
    # print(response.status_code, response.text)
