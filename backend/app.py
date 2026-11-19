"""
backend/app.py  — with PostgreSQL + SQLite fallback + JWT auth
"""
import os, sys

# ── CRITICAL: add backend/ to sys.path at module level (before any imports)
_BACKEND = os.path.abspath(os.path.dirname(__file__))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# These now resolve because _BACKEND is on sys.path
from models.db_models import db, bcrypt
from routes.predict_routes import predict_bp
from routes.info_routes    import info_bp
from routes.auth_routes    import auth_bp
from routes.history_routes import history_bp


def create_app():
    _FRONTEND = os.path.join(_BACKEND, '..', 'frontend')
    app = Flask(__name__, static_folder=os.path.abspath(_FRONTEND), static_url_path='')

    # ── Database ──────────────────────────────────────────────────────────
    DB_PATH      = os.path.join(_BACKEND, 'medpredict.db')
    database_url = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    app.config['JWT_SECRET_KEY']                 = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI']        = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    # ── Blueprints ────────────────────────────────────────────────────────
    app.register_blueprint(predict_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)

    # ── Frontend ──────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # ── DB tables ─────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    create_app().run(host='0.0.0.0', port=port, debug=False)
