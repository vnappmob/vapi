"""app/api/gold.py"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_gold', __name__)  # pylint: disable=C


@bp.route('/api/gold/sjc', methods=['POST'])
def api_vbiz_post():
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
                vals = []
                statements = (
                    "INSERT INTO vnappmob_gold_sjc "
                    "(id, buy_1l, sell_1l, buy_1c, "
                    "sell_1c, buy_nhan1c, sell_nhan1c, buy_trangsuc49, "
                    "sell_trangsuc49) "
                    "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s);")
                vals.extend((json_data['buy_1l'], json_data['sell_1l'],
                             json_data['buy_1c'], json_data['sell_1c'],
                             json_data['buy_nhan1c'], json_data['sell_nhan1c'],
                             json_data['buy_trangsuc49'],
                             json_data['sell_trangsuc49']))
                db_connect.writecommit(statements, tuple(vals))
                return make_response((jsonify({'results': 201})), 201)
            return error_response(403, 'API <---> Data')
        except MySQLdb.Error as err:  # pylint: disable=E
            return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
