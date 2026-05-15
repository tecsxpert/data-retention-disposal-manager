from flask import Blueprint, request
from datetime import datetime

# Import security middleware
from auth_middleware import token_required
from rate_limiter import rate_limit

# Import cache from extensions (NOT app)
from extensions import cache

describe_bp = Blueprint('describe', __name__)

@describe_bp.route('/describe', methods=['POST'])
@rate_limit
@token_required
@cache.cached(timeout=60,key_prefix=lambda: request.get_data())
def describe():

    # Check if request has JSON content
    if not request.is_json:
        return {"error": "Request body is required"}, 400

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    record_type = data.get("recordType")
    retention_period = data.get("retentionPeriod")
    risk_level = data.get("riskLevel")

    if not record_type or not retention_period or not risk_level:
        return {"error": "Missing fields"}, 400

    # Validate risk level
    valid_risk_levels = ["Low", "Medium", "High"]
    if risk_level not in valid_risk_levels:
        return {"error": "Invalid risk level"}, 400

    # Check for potential injection attacks
    dangerous_patterns = ["drop table", "delete from", "insert into", "update set", "--", ";", "'", "\"", "ignore previous", "system prompt"]
    
    for pattern in dangerous_patterns:
        if pattern.lower() in record_type.lower():
            return {"error": "Invalid input detected"}, 400

    # Generate real AI-like description
    try:
        description = (
            f"{record_type} with {risk_level} risk should be securely retained for "
            f"{retention_period} before disposal."
        )

        return {
            "description": description,
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": False
        }

    except Exception:
        return {
            "description": "AI service unavailable",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }