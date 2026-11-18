"""
backend/app.py  — with PostgreSQL + SQLite fallback + JWT auth
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models.db_models import db, bcrypt


def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')

    # ── Database URI ───────────────────────────────────────────────────────
    # Render gives DATABASE_URL as postgres://... but SQLAlchemy needs postgresql://
    BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
    DB_PATH     = os.path.join(BASE_DIR, 'medpredict.db')
    database_url = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    if database_url.startswith('postgres://'):          # fix Render's URL scheme
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    # ── Config ────────────────────────────────────────────────────────────
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
    from routes.predict_routes import predict_bp
    from routes.info_routes    import info_bp
    from routes.auth_routes    import auth_bp
    from routes.history_routes import history_bp

    app.register_blueprint(predict_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)

    # ── Serve frontend at / ────────────────────────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # ── Create tables ──────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app  = create_app()
    app.run(host='0.0.0.0', port=port, debug=False)
