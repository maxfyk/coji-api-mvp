from modules.db_operations import init_db_app

init_db_app()

from flask import Flask
from flask_cors import CORS

from services.coji_create import coji_create_bp
from services.coji_decode import coji_decode_bp
from services.prometheus_metrics import prometheus_metrics
from services.other import other

app = Flask(__name__)
CORS(app)

app.register_blueprint(coji_create_bp, url_prefix='/coji-code')
app.register_blueprint(coji_decode_bp, url_prefix='/coji-code')
app.register_blueprint(other, url_prefix='/coji-code')
app.register_blueprint(prometheus_metrics)

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
