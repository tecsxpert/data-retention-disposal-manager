# Import Blueprint and request for API handling
from flask import Blueprint, request, jsonify

# Import datetime to add timestamp
from datetime import datetime

# Import Groq client (AI service)
from services.groq_client import GroqClient

# Import os to read prompt file
import os

# Create blueprint
describe_bp = Blueprint('describe', __name__)


# Create POST endpoint
@describe_bp.route('/describe', methods=['POST'])
@cache.cached(timeout=60,key_prefix=lambda: request.get_data())
def describe():

    # Read JSON input safely
    data = request.get_json(silent=True)

    # Validate if body exists
    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Extract fields
    record_type = data.get("recordType")
    retention_period = data.get("retentionPeriod")
    risk_level = data.get("riskLevel")

    if not record_type or not retention_period or not risk_level:
        return jsonify({
            "error": "recordType, retentionPeriod and riskLevel are required"
        }), 400

    try:
        # -------------------------------
        # STEP 1: Load prompt template
        # -------------------------------
        base_dir = os.path.dirname(os.path.abspath(__file__))

        prompt_path = os.path.normpath(
            os.path.join(base_dir, "..", "prompts", "describe_prompt.txt")
        )

        if not os.path.exists(prompt_path):
            raise FileNotFoundError("Prompt file not found")

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_template = file.read()

        # -------------------------------
        # STEP 2: Create prompt
        # -------------------------------
        prompt = prompt_template.format(
            record_type=record_type,
            retention_period=retention_period,
            risk_level=risk_level
        )

        # -------------------------------
        # STEP 3: Call AI
        # -------------------------------
        groq_client = GroqClient()
        ai_response = groq_client.generate_response(prompt)

        # -------------------------------
        # STEP 4: Handle response
        # -------------------------------
        if not ai_response.get("success"):
            return jsonify({
                "description": "AI service unavailable",
                "generated_at": datetime.utcnow().isoformat(),
                "is_fallback": True
            }), 200

        return jsonify({
            "description": ai_response.get("data", "").strip(),
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": False
        }), 200

    except Exception as e:
        # 🔥 IMPORTANT: show actual error (for debugging)
        print("ERROR:", str(e))

        return jsonify({
            "description": str(e),   # show real issue
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }), 500