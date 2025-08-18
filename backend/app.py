from flask import Flask
from flask_cors import CORS
from backend.routes import routes_bp
from backend.payments import payments_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(routes_bp, url_prefix="/api")
    app.register_blueprint(payments_bp, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
