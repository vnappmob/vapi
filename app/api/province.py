"""app/api/province.py"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_province', __name__)  # pylint: disable=C


@bp.route('/api/province/', methods=['GET'])
def api_province_get():
    """
    Retrieve a list of province
    ```
    [GET] /api/province
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = ("SELECT * FROM vnappmob_list_province ORDER BY province_name;")
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/province/<string:province_id>/', methods=['GET'])
@bp.route('/api/province/<string:province_id>/district/', methods=['GET'])
def api_district_get(province_id):
    """
    Retrieve a list of district in province_id
    ```
    [GET] /api/province/{province_id}/
    [GET] /api/province/{province_id}/district
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = (
                "SELECT * FROM vnappmob_list_district WHERE province_id = '" + province_id + "' ORDER BY district_name;")
            print(statements)
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/province/<string:province_id>/<string:district_id>/', methods=['GET'])
@bp.route('/api/province/<string:province_id>/district/<string:district_id>/', methods=['GET'])
@bp.route('/api/province/<string:province_id>/district/<string:district_id>/ward/', methods=['GET'])
def api_ward_get(province_id, district_id):
    """
    Retrieve a list of ward in district_id
    ```
    [GET] /api/province/{province_id}/{district_id}/
    [GET] /api/province/{province_id}/district/{district_id}/
    [GET] /api/province/{province_id}/district/{district_id}/ward
    ```
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = (
                "SELECT * FROM vnappmob_list_ward WHERE district_id = '" + district_id + "' ORDER BY ward_name;")
            print(statements)
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
