# backend/app.py
import sys
from flask import Flask
from flask_cors import CORS

# Allow running both as package (-m) and script (python backend/app.py)
try:
    from backend.routes import routes_bp
    from backend.payments import payments_bp
except ModuleNotFoundError:
    # add project root to sys.path if run directly
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
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
    # You can run either:
    #   python -m backend.app
    # or:
    #   python backend/app.py
    app.run(debug=True, port=5000)
