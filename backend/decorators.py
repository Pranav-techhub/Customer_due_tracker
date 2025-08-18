from functools import wraps
from flask import request, jsonify

# Simple example decorator for API key protection (optional)
def require_api_key(param_name="x-api-key", expected=None):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = request.headers.get(param_name)
            if expected and key != expected:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return wrapper
    return deco
