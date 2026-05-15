import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import secrets

# Secret key for JWT (in production, use environment variable)
JWT_SECRET = secrets.token_urlsafe(32)
JWT_ALGORITHM = 'HS256'

def generate_token():
    """Generate a JWT token for testing"""
    payload = {
        'user': 'test_user',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require JWT token for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For testing, allow requests without token but mark them
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Authorization token is required',
                'code': 'TOKEN_MISSING'
            }), 401
        
        try:
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        except IndexError:
            return jsonify({
                'error': 'Invalid authorization header format',
                'code': 'TOKEN_INVALID_FORMAT'
            }), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'TOKEN_INVALID'
            }), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

# Export for testing
JWT_SECRET = JWT_SECRET
