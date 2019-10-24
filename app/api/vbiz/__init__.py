# -*- coding: utf-8 -*-
"""app/api/vbiz.py
"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response

bp = Blueprint('api_vbiz', __name__)  # pylint: disable=C


@bp.route('/api/vbiz/search/<string:keyword>', methods=['GET'])
def api_vbiz_search(keyword):
    """.. :quickref: 01. vBiz; Find business by {vbiz_code} or {vbiz_name}

    This function allows users to search Vietnamese businesses by 
    business tax's ID or by business name

    **Request**:

    .. sourcecode:: http

      GET /api/vbiz/search/{keyword} HTTP/1.1
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
                  "vbiz_name": "",
                  "vbiz_code": ""
              }
          ]
      }

    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect(db='vbiz_db')
    if db_connect.connected:
        try:
            if keyword.isdigit():
                statements = (
                    "SELECT vbiz_code, vbiz_name "
                    "FROM vbiz "
                    "WHERE vbiz_code like '" + keyword + "%%' LIMIT 0, 10")
            elif len(keyword) < 16:
                statements = (
                    "SELECT vbiz_code, vbiz_name FROM vbiz "
                    "WHERE match(vbiz_name) "
                    "AGAINST ('\"" + keyword + "\"' IN NATURAL LANGUAGE MODE) LIMIT 0, 10")
            else:
                statements = (
                    "SELECT vbiz_code, vbiz_name "
                    "FROM vbiz "
                    "WHERE vbiz_name like '" + keyword + "%%' LIMIT 0, 10")

            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))


@bp.route('/api/vbiz/<string:vbiz_code>', methods=['GET'])
def api_vbiz_get(vbiz_code):
    """.. :quickref: 02. vBiz; Get business details with {vbiz_code}

    This function allows users to get Vietnamese business information
    followed by business tax's ID

    **Request**:

    .. sourcecode:: http

      GET /api/vbiz/{vbiz_code} HTTP/1.1
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
                  "vbiz_code": "",
                  "vbiz_address": "",
                  "vbiz_phone": "",
                  "vbiz_email": "",
                  "vbiz_website": "",
                  "vbiz_register_date": ""
              }
          ]
      }

    :resheader Content-Type: application/json
    :status 200: results
    """
    db_connect = VDBConnect(db='vbiz_db')
    if db_connect.connected:
        try:
            statements = (
                "SELECT * FROM `vbiz` where vbiz_code = '" + vbiz_code + "'")
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
