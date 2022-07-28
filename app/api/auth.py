import datetime
from functools import wraps

import jwt
from flask import current_app, request

from app.errors import error_response


def require_api_key(scope='', permission=0):
    def actual_decorator(func):
        @wraps(func)
        def check_api_key(*args, **kwargs):
            api_key = False
            if request.headers.get('Authorization'):
                api_key = request.headers['Authorization'].split(" ")[1]
            elif request.args.get('api_key'):
                api_key = request.args.get('api_key')

            try:
                if not api_key:
                    raise Exception('No api_key')

                payload = jwt.decode(
                    api_key,
                    current_app.config.get('SECRET_KEY'),
                    algorithms=['HS256']
                )

                if payload['scope'] != '*' and payload['scope'] != scope:
                    raise Exception('Out of scope')

                if permission > int(payload['permission']):
                    raise Exception('No permission')

                return func(*args, **kwargs)

            except Exception as e:
                return error_response(403, 'Auth Error: %s' % (e))

        return check_api_key
    return actual_decorator


def generate_api_key(**kwargs):
    """
    Generates the Auth Token
    :scope: string | (gold, exchange_rate)
    :permission: int | 0:r | 1:rw | 2:rwd
    :return: string
    """
    try:
        scope = kwargs['scope'] if 'scope' in kwargs and kwargs['scope'] is not None else '*'
        permission = kwargs['permission'] if 'permission' in kwargs and kwargs['permission'] is not None else 0
        dtl = int(
            kwargs['dtl']) if 'dtl' in kwargs and kwargs['dtl'] is not None else 15

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=dtl),
            'iat': datetime.datetime.utcnow(),
            'scope': scope,
            'permission': permission
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e
