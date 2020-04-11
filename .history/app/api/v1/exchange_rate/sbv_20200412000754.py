"""app/api/exchange_rate/sbv.py"""
from collections import defaultdict
import requests
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response
from app.api.v1.exchange_rate import bp


@bp.route('/api/exchange_rate/sbv', methods=['GET'])
def api_exchange_rate_sbv_get():
    """.. :quickref: 02. SBV; Get all SBV exchange rate

    This function allows users to get the latest exchange rate from
    State Bank of Vietnam

    **Request**:

    .. sourcecode:: http

      GET /api/exchange_rate/sbv HTTP/1.1
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
                    'SELECT t1.currency, t1.buy, t1.sell '
                    'FROM vnappmob_exchange_rate_sbv t1 '
                    'WHERE id IN ( '
                    'SELECT MAX(id) FROM vnappmob_exchange_rate_sbv '
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


@bp.route('/api/exchange_rate/sbv', methods=['POST'])
def api_exchange_rate_sbv_post():
    """.. :quickref: 02. SBV; Post new exchange rate

    Limited function that allows data manager to push newest price

    **Request**:

    .. sourcecode:: http

      POST /api/exchange_rate/sbv HTTP/1.1
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
    :<json float buy: buy
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
                    'SELECT t1.currency, t1.buy, t1.sell '
                    'FROM vnappmob_exchange_rate_sbv t1 '
                    'WHERE id IN ( '
                    'SELECT MAX(id) FROM vnappmob_exchange_rate_sbv '
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
                    buy = post_data['buy']
                    sell = post_data['sell']
                    latest_data = latest_datas_dict[currency]

                    if latest_data:
                        if any([
                                float(latest_data['buy']) != float(buy),
                                float(latest_data['sell']) != float(sell),
                        ]):
                            changed_list.append(currency)
                            insert_new_data(db_connect, currency, buy, sell)
                    else:
                        changed_list.append(currency)
                        insert_new_data(db_connect, currency, buy, sell)

                if changed_list:
                    print(changed_list)
                    return make_response((jsonify({'results': 201})), 201)
                return make_response((jsonify({'results': 200})), 200)
            return error_response(403, 'Invalid api_key')
        except MySQLdb.Error as err:  # pylint: disable=E
            return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


def insert_new_data(db_connect, currency, buy, sell):
    """insert_new_data"""
    vals = []
    statements = ("INSERT INTO vnappmob_exchange_rate_sbv "
                  "(id, currency, buy, sell) "
                  "VALUES (NULL, %s, %s, %s);")
    vals.extend((currency, buy, sell))
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
    # data = ()
    #
    # response = requests.post(
    #     'https://fcm.googleapis.com/fcm/send',
    #     headers=headers,
    #     data=data.encode('utf-8'))
    # print(response.status_code, response.text)
