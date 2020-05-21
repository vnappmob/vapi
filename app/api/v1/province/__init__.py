# -*- coding: utf-8 -*-
""".. :quickref:
This module allows users to get a list of province, district & ward in Vietnam
"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_province', __name__)  # pylint: disable=C


@bp.route('/api/province/', methods=['GET'])
def api_province_get():
    """.. :quickref: 01. Province; Get list of provinces

    This function allows users to get a list of provinces in Vietnam

    **Request**:

    .. sourcecode:: http

      GET /api/province HTTP/1.1
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
                  "province_id": 92,
                  "province_name": "Th\u00e0nh ph\u1ed1 H\u00e0 N\u1ed9i",
                  "province_type": "Th\u00e0nh ph\u1ed1 Trung \u01b0\u01a1ng"
              }
          ]
      }

    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = ("SELECT * FROM vnappmob_list_province "
                          "ORDER BY province_name "
                          "COLLATE utf8_vietnamese_ci;")
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/province/district/<string:province_id>', methods=['GET'])
def api_district_get(province_id):
    """.. :quickref: 02. District; Get list of districts with {province_id}

    This function allows users to get a list of districts in Vietnam
    followed by {province_id}

    **Request**:

    .. sourcecode:: http

      GET /api/province/district/{province_id} HTTP/1.1
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
                  "district_id": 271,
                  "district_name": "Huy\u1ec7n Ba V\u00ec"
              }
          ]
      }

    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = (
                "SELECT district_id, district_name, district_type, province_id, "
                "X(location) AS lat, Y(location) AS lng "
                "FROM vnappmob_list_district WHERE province_id = '" +
                province_id +
                "' ORDER BY district_name COLLATE utf8_vietnamese_ci;")
            print(statements)
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/province/ward/<string:district_id>', methods=['GET'])
def api_ward_get(district_id):
    """.. :quickref: 03. Ward; Get list of wards with {district_id}

    This function allows users to get a list of wards in Vietnam
    followed by {district_id}

    **Request**:

    .. sourcecode:: http

      GET /api/province/ward/{district_id} HTTP/1.1
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
                  "ward_id": 271,
                  "ward_name": "Th\u1ecb tr\u1ea5n T\u00e2y \u0110\u1eb1ng"
              }
          ]
      }

    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect()
    if db_connect.connected:
        try:
            statements = (
                "SELECT * FROM vnappmob_list_ward WHERE district_id = '" +
                district_id +
                "' ORDER BY ward_name COLLATE utf8_vietnamese_ci;")
            print(statements)
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
