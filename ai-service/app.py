# Import Flask class
from flask import Flask

# Import cache from extensions
from extensions import cache

# Create Flask application
app = Flask(__name__)

# Configure cache
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes

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
    return {
        "status": "working"
    }


# Add security headers
@app.after_request
def add_security_headers(response):

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"

    return response


# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
