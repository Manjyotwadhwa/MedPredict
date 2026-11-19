import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
    app = Flask(__name__, static_folder=os.path.abspath(FRONTEND_DIR), static_url_path='')
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    from routes.predict_routes import predict_bp
    from routes.info_routes import info_bp
    app.register_blueprint(predict_bp)
    app.register_blueprint(info_bp)
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    create_app().run(host='0.0.0.0', port=port, debug=False)