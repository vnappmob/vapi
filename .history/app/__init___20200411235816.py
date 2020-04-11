"""app/__init__.py"""
import os
import time
from flask import Flask, Request, request

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response
from app.api.province import bp as api_province_bp
from app.api.gold import bp as api_gold_bp
from app.api.exchange_rate import bp as api_exchange_rate_bp
from app.api.vbiz import bp as api_vbiz_bp

FLASK_ENV = os.environ.get("FLASK_ENV", default='production')
if FLASK_ENV == 'development':
    from config import DevelopmentConfig as AppConfig
elif FLASK_ENV == 'testing':
    from config import TestingConfig as AppConfig
else:
    from config import ProductionConfig as AppConfig


class ProxiedRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        super().__init__(environ, populate_request, shallow)
        x_forwarded_proto = self.headers.get('X-Forwarded-Proto')
        if x_forwarded_proto == 'https':
            self.url = self.url.replace('http://', 'https://')
            self.host_url = self.host_url.replace('http://', 'https://')
            self.base_url = self.base_url.replace('http://', 'https://')
            self.url_root = self.url_root.replace('http://', 'https://')


app = Flask(__name__, static_url_path='/',
            static_folder='_build/html/')  # pylint: disable=C
CORS(app)
limiter = Limiter(app, key_func=get_remote_address)
app.request_class = ProxiedRequest
app.config.from_object(AppConfig)

app.register_blueprint(api_province_bp)
app.register_blueprint(api_gold_bp)
app.register_blueprint(api_exchange_rate_bp)
app.register_blueprint(api_vbiz_bp)

CURRENT_YEAR = time.strftime("%Y")
BASE_TITLE = ('vAPI - Open API for Vietnamese projects')
BASE_DESCRIPTION = ('Open API for Vietnamese projects')
BASE_PHOTO = ('https://vnappmob.sgp1.cdn.digitaloceanspaces.com'
              '/vnappmob/assets/img/vapi_photo.png')

# just4fun


@app.route('/')
@app.route('/<path:path>')
def static_file(path):
    """static_file"""
    return app.send_static_file(path)


# @app.route('/')
# def index():
#     """index"""
#     return 'Hello - Please refer to the documentations on https://vapi-vnappmob.readthedocs.io/en/latest/'
