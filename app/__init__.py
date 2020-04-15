"""app/__init__.py"""
import os
import time
from flask import g, Flask, Request, request

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.api.auth import generate_api_key
from app.db.db_connect import VDBConnect, MySQLdb
from app.errors import error_response
from app.api.v1.province import bp as api_province_bp
from app.api.v1.gold import bp as api_gold_bp
from app.api.v2.gold import bp as api_v2_gold_bp
from app.api.v1.exchange_rate import bp as api_exchange_rate_bp
from app.api.v1.vbiz import bp as api_vbiz_bp

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
            static_folder='../docs/build/html/')  # pylint: disable=C
CORS(app)
limiter = Limiter(app, key_func=get_remote_address)
app.request_class = ProxiedRequest
app.config.from_object(AppConfig)

app.register_blueprint(api_province_bp)
app.register_blueprint(api_gold_bp)
app.register_blueprint(api_v2_gold_bp)
app.register_blueprint(api_exchange_rate_bp)
app.register_blueprint(api_vbiz_bp)

CURRENT_YEAR = time.strftime("%Y")
BASE_TITLE = ('vAPI - Open API for Vietnamese projects')
BASE_DESCRIPTION = ('Open API for Vietnamese projects')


@app.route('/')
@app.route('/<path:path>')
def static_file(path='index.html'):
    """static_file"""
    return app.send_static_file(path)


@app.route('/api/request_api_key')
def request_api_key():
    scope = request.args.get('scope')
    permission = request.args.get('permission')
    dtl = request.args.get('dtl')
    return generate_api_key(scope, permission, dtl)


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    print('total: %s' % (time.time() - g.start))
    return response
