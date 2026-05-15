# Import Blueprint and request
from flask import Blueprint, request

# Import datetime for timestamp
from datetime import datetime

# Import security middleware
from auth_middleware import token_required
from rate_limiter import rate_limit

# Create blueprint
report_bp = Blueprint('report', __name__)


# Create POST endpoint
@report_bp.route('/generate-report', methods=['POST'])
@rate_limit
@token_required
def generate_report():

    # Check if request has JSON content
    if not request.is_json:
        return {"error": "Request body is required"}, 400

    # Read request JSON
    data = request.get_json()

    # Validate input
    if not data:
        return {"error": "Request body is required"}, 400

    # Extract fields
    record_type = data.get("recordType")
    retention_period = data.get("retentionPeriod")
    risk_level = data.get("riskLevel")

    # Validate fields
    if not record_type or not retention_period or not risk_level:
        return {
            "error": "recordType, retentionPeriod and riskLevel are required"
        }, 400

    # Validate risk level
    valid_risk_levels = ["Low", "Medium", "High"]
    if risk_level not in valid_risk_levels:
        return {"error": "Invalid risk level"}, 400

    # Check for potential injection attacks
    dangerous_patterns = ["drop table", "delete from", "insert into", "update set", "--", ";", "'", "\"", "ignore previous", "system prompt"]
    
    for pattern in dangerous_patterns:
        if pattern.lower() in record_type.lower():
            return {"error": "Invalid input detected"}, 400

    # Generate real AI-like report
    try:
        # 🔥 Dynamic report generation

        title = f"{record_type} Retention Report"

        summary = (
            f"{record_type} requires careful handling due to its {risk_level} risk level."
        )

        overview = (
            f"{record_type} should be securely retained for {retention_period} "
            f"and managed according to compliance standards."
        )

        key_items = [
            f"Record Type: {record_type}",
            f"Retention Period: {retention_period}",
            f"Risk Level: {risk_level}"
        ]

        # Dynamic recommendations based on risk
        if risk_level == "High":
            recommendations = [
                "Apply strict access control policies",
                "Encrypt sensitive data at rest and in transit",
                f"Ensure secure deletion after {retention_period}"
            ]

        elif risk_level == "Medium":
            recommendations = [
                "Archive data securely",
                "Perform periodic compliance reviews",
                f"Delete data after {retention_period}"
            ]

        else:  # Low risk
            recommendations = [
                "Store data with basic protection",
                "Monitor usage occasionally",
                f"Delete data after {retention_period}"
            ]

        # Final response
        report = {
            "title": title,
            "summary": summary,
            "overview": overview,
            "key_items": key_items,
            "recommendations": recommendations
        }

        return {
            "report": report,
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": False
        }

    except Exception:
        return {
            "report": {},
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }