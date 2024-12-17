# -*- coding: utf-8 -*-
""".. :quickref:
This module allows users to get a list of province, district & ward in Vietnam
"""
from flask import Blueprint, request, make_response, jsonify, current_app  # pylint: disable=W
from app.db.mongodb_connect import MongoDBConnect
from app.errors import error_response

bp = Blueprint('api_v2_province', __name__)  # pylint: disable=C


@bp.route('/api/v2/province/', methods=['GET'])
def api_province_get():
    """.. :quickref: 01. Province; Get list of provinces

    This function allows users to get a list of provinces in Vietnam

    **Request**:

    .. sourcecode:: http

      GET /api/v2/province HTTP/1.1
      Host: https://api.vnappmob.com
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
    try:
        db_connect = MongoDBConnect()
        db = 'province_db'
        collection = 'province'
        
        q_res = db_connect.connection[db][collection].find(
            filter={},
            projection={
                '_id': False
            },
            sort=list({
                'province_type': 1
            }.items())
        )

        results = list(q_res)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()


@bp.route('/api/v2/province/district/<string:province_id>', methods=['GET'])
def api_district_get(province_id):
    """.. :quickref: 02. District; Get list of districts with {province_id}

    This function allows users to get a list of districts in Vietnam
    followed by {province_id}

    **Request**:

    .. sourcecode:: http

      GET /api/v2/province/district/{province_id} HTTP/1.1
      Host: https://api.vnappmob.com
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
    try:
        db_connect = MongoDBConnect()
        db = 'province_db'
        collection = 'district'
        
        q_res = db_connect.connection[db][collection].find(
            filter={
                'province_id': province_id
            },
            projection={
                '_id': False
            },
            sort=list({
                'district_id': 1
            }.items())
        )

        results = list(q_res)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
    


@bp.route('/api/v2/province/ward/<string:district_id>', methods=['GET'])
def api_ward_get(district_id):
    """.. :quickref: 03. Ward; Get list of wards with {district_id}

    This function allows users to get a list of wards in Vietnam
    followed by {district_id}

    **Request**:

    .. sourcecode:: http

      GET /api/v2/province/ward/{district_id} HTTP/1.1
      Host: https://api.vnappmob.com
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
    try:
        db_connect = MongoDBConnect()
        db = 'province_db'
        collection = 'ward'
        
        q_res = db_connect.connection[db][collection].find(
            filter={
                'district_id': district_id
            },
            projection={
                '_id': False
            },
            sort=list({
                'ward_id': 1
            }.items())
        )

        results = list(q_res)

        responses = {
            'results': results
        }

        return make_response((jsonify(responses)), 200)
    except Exception as e:
        return error_response(400, str(e))
    finally:
        db_connect.connection.close()
    
