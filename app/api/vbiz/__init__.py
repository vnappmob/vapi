# -*- coding: utf-8 -*-
"""app/api/vbiz.py
"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response
from app.helper.VietnameseHelper import VietnameseHelper

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
                    "WHERE vbiz_code like '" + keyword + "%%' "
                    "LIMIT 0, 5")
            else:
                vh = VietnameseHelper()
                cw = set([b'cong', b'cong ty', b'cong ty tnhh',
                          b'cong ty co', b'cong ty co phan',
                          b'doanh', b'doanh nghiep'])
                if len(keyword) > 16 or cw.intersection(set(word for word in vh.no_accent_lower(keyword).split())):
                    statements = (
                        "SELECT vbiz_code, vbiz_name "
                        "FROM vbiz "
                        "WHERE vbiz_name like '" + keyword + "%%' "
                        "LIMIT 0, 5")
                else:
                    statements = (
                        "SELECT vbiz_code, vbiz_name FROM vbiz "
                        "WHERE match(vbiz_name) "
                        "AGAINST ('\"" + keyword +
                        "\"' IN NATURAL LANGUAGE MODE) "
                        "LIMIT 0, 5")

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


@bp.route('/api/vbiz/cat/<string:vbiz_category_id>', methods=['GET'])
def api_vbiz_get(vbiz_category_id):
    """.. :quickref: 03. vBiz; Get list business with {vbiz_category_id}

    This function allows users to get list of Vietnamese business information
    followed by business category

    **Request**:

    .. sourcecode:: http

      GET /api/vbiz/cat/{vbiz_category_id} HTTP/1.1
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
            per_page = request.args.get('per_page', default=10, type=int)
            page = request.args.get('page', default='1', type=int)
            date_from = request.args.get('date_from', default=0, type=int)
            date_to = request.args.get('date_to', default=0, type=int)
            filter_phone = request.args.get(
                'filter_phone', default=False, type=bool)
            filter_email = request.args.get(
                'filter_email', default=False, type=bool)

            extras_where += " AND vbiz_phone <> '' " if filter_phone else " "
            extras_where += " AND vbiz_email <> '' " if filter_email else " "

            statements = (
                "SELECT t1.* "
                "FROM vbiz t1"
                "WHERE t1.vbiz_category_id = '" + vbiz_category_id + "' "
                "AND t1.vbiz_register_date > '" + date_from + "' "
                "AND t1.vbiz_register_date < '" + date_to + "' " + extras_where + " "
                "ORDER BY t1.vbiz_register_timestamp DESC, t1.vbiz_update_timestamp DESC "
                "LIMIT " + str((page - 1) * per_page) + ", " + str(per_page) + ";")
            try:
                results = db_connect.readall(statements)
                return make_response((jsonify({'results': results})), 200)
            except MySQLdb.Error as err:  # pylint: disable=E
                return error_response(400, str(err))
        finally:
            db_connect.close()
    return error_response(404, str(db_connect.error))
