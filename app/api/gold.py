"""app/api/gold.py"""
import requests
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_gold', __name__)  # pylint: disable=C


@bp.route('/api/gold/sjc', methods=['GET'])
def api_gold_sjc_get():
    """
    ```
    [GET] /api/gold/sjc?api_key={api_key}&date_from={date_from}&date_to={date_to}
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.args.get('api_key', default='', type=str)
            date_from = request.args.get('date_from', default=0, type=int)
            date_to = request.args.get('date_to', default=0, type=int)

            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:
                # SELECT * FROM `vnappmob_gold_sjc`
                # JOIN (
                #       SELECT MAX(t.datetime) AS datetime
                #       FROM vnappmob_gold_sjc AS t
                #       GROUP BY YEAR(t.datetime), MONTH(t.datetime), DATE(t.datetime)
                # ) AS x USING (datetime)
                statements = (
                    "SELECT UNIX_TIMESTAMP(t1.datetime) as datetime, "
                    "t1.buy_1l, t1.sell_1l, t1.buy_1c, t1.sell_1c, "
                    "t1.buy_nhan1c, t1.sell_nhan1c, t1.buy_trangsuc49, t1.sell_trangsuc49 "
                    "FROM vnappmob_gold_sjc t1 "
                    "ORDER BY id DESC LIMIT 1;")
                try:
                    results = db_connect.readall(statements)
                    return make_response((jsonify({'results': results})), 200)
                except MySQLdb.Error as err:  # pylint: disable=E
                    return error_response(400, str(err))
            return error_response(403, 'Invalid api_key')
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/gold/sjc', methods=['POST'])
def api_gold_sjc_post():
    """
    New gold_sjc record
    ```
    [POST] /api/gold/sjc
        -H 'Authorization: {api_key}'
        -H 'Content-Type: application/json'
        --data '{
                    "buy_1l": "{}",
                    "sell_1l": "{}",
                    "buy_1c": "{}",
                    "sell_1c": "{}",
                    "buy_nhan1c": "{}",
                    "sell_nhan1c": "{}",
                    "buy_trangsuc49": "{}",
                    "sell_trangsuc49": "{}"
                }'
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.headers['Authorization']
            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:
                json_data = request.get_json()

                last_row = db_connect.readone(
                    "SELECT * FROM vnappmob_gold_sjc "
                    "ORDER BY id DESC LIMIT 1;")
                if any([
                        float(last_row['buy_1l']) != float(
                            json_data['buy_1l']),
                        float(last_row['sell_1l']) != float(
                            json_data['sell_1l']),
                        float(last_row['buy_1c']) != float(
                            json_data['buy_1c']),
                        float(last_row['sell_1c']) != float(
                            json_data['sell_1c']),
                        float(last_row['buy_nhan1c']) != float(
                            json_data['buy_nhan1c']),
                        float(last_row['sell_nhan1c']) != float(
                            json_data['sell_nhan1c']),
                        float(last_row['buy_trangsuc49']) != float(
                            json_data['buy_trangsuc49']),
                        float(last_row['sell_trangsuc49']) != float(
                            json_data['sell_trangsuc49'])
                ]):
                    vals = []
                    statements = (
                        "INSERT INTO vnappmob_gold_sjc "
                        "(id, buy_1l, sell_1l, buy_1c, "
                        "sell_1c, buy_nhan1c, sell_nhan1c, buy_trangsuc49, "
                        "sell_trangsuc49) "
                        "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s);")
                    vals.extend(
                        (json_data['buy_1l'], json_data['sell_1l'],
                         json_data['buy_1c'], json_data['sell_1c'],
                         json_data['buy_nhan1c'], json_data['sell_nhan1c'],
                         json_data['buy_trangsuc49'],
                         json_data['sell_trangsuc49']))
                    db_connect.writecommit(statements, tuple(vals))

                    headers = {
                        'Authorization':
                        'key=' + current_app.config['VPRICE_FCM_KEY'],
                        'Content-Type':
                        'application/json'
                    }

                    data = (
                        '{"notification": {"title": "vPrice - Biến động giá SJC"'
                        ',"body": "1L: Mua ' + '{:,d}'.format(
                            int(json_data['buy_1l'])) + ' - Bán ' +
                        '{:,d}'.format(int(json_data['sell_1l'])) +
                        ' ","sound": "default"},"priority": "high",'
                        '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                        '"id": "1","status": "done"},'
                        '"to": "/topics/sjcgold"}')

                    response = requests.post(
                        'https://fcm.googleapis.com/fcm/send',
                        headers=headers,
                        data=data.encode('utf-8'))
                    print(response.status_code, response.text)

                    return make_response((jsonify({'results': 201})), 201)
                return make_response((jsonify({'results': 200})), 200)
            return error_response(403, 'Invalid api_key')
        except MySQLdb.Error as err:  # pylint: disable=E
            return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/gold/doji', methods=['GET'])
def api_gold_doji_get():
    """
    ```
    [GET] /api/gold/doji?api_key={api_key}&date_from={date_from}&date_to={date_to}
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.args.get('api_key', default='', type=str)
            date_from = request.args.get('date_from', default=0, type=int)
            date_to = request.args.get('date_to', default=0, type=int)

            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:
                statements = (
                    "SELECT UNIX_TIMESTAMP(t1.datetime) as datetime, "
                    "t1.buy_hcm, t1.sell_hcm, t1.buy_hn, t1.sell_hn "
                    "FROM vnappmob_gold_doji t1 "
                    "ORDER BY id DESC LIMIT 1;")
                try:
                    results = db_connect.readall(statements)
                    return make_response((jsonify({'results': results})), 200)
                except MySQLdb.Error as err:  # pylint: disable=E
                    return error_response(400, str(err))
            return error_response(403, 'Invalid api_key')
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/gold/doji', methods=['POST'])
def api_gold_doji_post():
    """
    New gold_doji record
    ```
    [POST] /api/gold/doji
        -H 'Authorization: {api_key}'
        -H 'Content-Type: application/json'
        --data '{
                    "buy_hcm": "{}",
                    "sell_hcm": "{}"
                }'
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            request_api = request.headers['Authorization']
            slash_settings = db_connect.get_slash_setting()
            if slash_settings['api'] == request_api:
                json_data = request.get_json()

                last_row = db_connect.readone(
                    "SELECT * FROM vnappmob_gold_doji "
                    "ORDER BY id DESC LIMIT 1;")
                if any([
                        float(last_row['buy_hcm']) != float(
                            json_data['buy_hcm']),
                        float(last_row['sell_hcm']) != float(
                            json_data['sell_hcm']),
                        float(last_row['buy_hn']) != float(
                            json_data['buy_hn']),
                        float(last_row['sell_hn']) != float(
                            json_data['sell_hn'])
                ]):
                    vals = []
                    statements = ("INSERT INTO vnappmob_gold_doji "
                                  "(id, buy_hcm, sell_hcm, buy_hn, sell_hn) "
                                  "VALUES (NULL, %s, %s, %s, %s);")
                    vals.extend((json_data['buy_hcm'], json_data['sell_hcm'],
                                 json_data['buy_hn'], json_data['sell_hn']))
                    db_connect.writecommit(statements, tuple(vals))

                    headers = {
                        'Authorization':
                        'key=' + current_app.config['VPRICE_FCM_KEY'],
                        'Content-Type':
                        'application/json'
                    }

                    data = (
                        '{"notification": {"title": "vPrice - Biến động giá DOJI"'
                        ',"body": "HCM: Mua ' + '{:,d}'.format(
                            int(json_data['buy_hcm'])) + ' - Bán ' +
                        '{:,d}'.format(int(json_data['sell_hcm'])) +
                        ' \nHN: Mua ' + '{:,d}'.format(
                            int(json_data['buy_hn'])) + ' - Bán ' +
                        '{:,d}'.format(int(json_data['sell_hn'])) +
                        ' ","sound": "default"},"priority": "high",'
                        '"data": {"click_action": "FLUTTER_NOTIFICATION_CLICK",'
                        '"id": "1","status": "done"},'
                        '"to": "/topics/dojigold"}')

                    response = requests.post(
                        'https://fcm.googleapis.com/fcm/send',
                        headers=headers,
                        data=data.encode('utf-8'))
                    print(response.status_code, response.text)

                    return make_response((jsonify({'results': 201})), 201)
                return make_response((jsonify({'results': 200})), 200)
            return error_response(403, 'Invalid api_key')
        except MySQLdb.Error as err:  # pylint: disable=E
            return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
