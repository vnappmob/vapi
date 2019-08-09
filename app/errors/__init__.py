"""app/errors.py"""
from flask import render_template, Blueprint, make_response, jsonify
from werkzeug.http import HTTP_STATUS_CODES

bp = Blueprint('errors', __name__)  #pylint: disable=C


def error_response(status_code, message=None):
    """error_response"""
    payload = {
        'error':
        str(status_code) + " - " + HTTP_STATUS_CODES.get(
            status_code, 'Unknown error')
    }
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@bp.app_errorhandler(400)
def error_400(error):  #pylint: disable=W
    """400"""
    return error_response(400)


@bp.app_errorhandler(404)
def error_404(error):  #pylint: disable=W
    """404"""
    return error_response(404)


@bp.app_errorhandler(405)
def error_405(error):  #pylint: disable=W
    """405"""
    return error_response(405)


@bp.app_errorhandler(429)
def error_429(error):  #pylint: disable=W
    """429"""
    return error_response(429)


@bp.app_errorhandler(500)
def internal_error(error):  #pylint: disable=W
    """500"""
    return error_response(500)
