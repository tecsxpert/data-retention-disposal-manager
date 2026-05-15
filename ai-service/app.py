# Import Flask class
from flask import Flask

# Import cache from extensions
from extensions import cache

# Import security middleware
from auth_middleware import token_required, generate_token, JWT_SECRET
from rate_limiter import rate_limit

# Create Flask application
app = Flask(__name__)

# Record start time for uptime calculation
import time
app.start_time = time.time()

# Configure cache and security
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes
app.config['JWT_SECRET'] = JWT_SECRET

# Initialize cache
cache.init_app(app)


# 🔹 Simulate model loading (Flask 3 compatible)
def load_model():
    print("AI Model loaded successfully...")


# Call it once at startup
load_model()


# Import routes AFTER app creation (important)
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

# Register routes
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)


# Health check route
@app.route('/health')
def health():
    import time
    start_time = getattr(app, 'start_time', time.time())
    uptime = int(time.time() - start_time)
    
    return {
        "status": "working",
        "model": "fallback-mock",
        "uptime_seconds": uptime
    }

# Token generation endpoint for testing
@app.route('/auth/token', methods=['POST'])
def get_token():
    return {
        "token": generate_token(),
        "type": "Bearer",
        "expires_in": 3600
    }


# Add security headers
@app.after_request
def add_security_headers(response):

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Enhanced CSP with all required directives
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self'; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    )
    
    # Suppress server information
    response.headers['Server'] = 'Apache'
    
    return response


# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)