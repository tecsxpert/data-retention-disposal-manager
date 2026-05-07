from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify

# Import blueprints
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

# Create Flask app
app = Flask(__name__)

# -------------------------------
# Register Blueprints (with prefix)
# -------------------------------
app.register_blueprint(describe_bp, url_prefix='/api')
app.register_blueprint(recommend_bp, url_prefix='/api')
app.register_blueprint(report_bp, url_prefix='/api')

# -------------------------------
# Health check route
# -------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "working",
        "service": "data-retention-ai"
    })

# -------------------------------
# Root route (prevents 404 confusion)
# -------------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Data Retention AI Service is running",
        "endpoints": [
            "/api/describe",
            "/api/recommend",
            "/api/report"
        ]
    })

# -------------------------------
# Run server
# -------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)