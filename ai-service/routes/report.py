from flask import Blueprint, request, jsonify
from datetime import datetime
from services.groq_client import GroqClient
import os
import json
import re

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['POST'])
def report():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    record_type = data.get("recordType")
    retention_period = data.get("retentionPeriod")
    risk_level = data.get("riskLevel")

    if not record_type or not retention_period or not risk_level:
        return jsonify({
            "error": "recordType, retentionPeriod and riskLevel are required"
        }), 400

    try:
        # -------------------------------
        # Load prompt
        # -------------------------------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.normpath(
            os.path.join(base_dir, "..", "prompts", "report_prompt.txt")
        )

        if not os.path.exists(prompt_path):
            return jsonify({"error": "Prompt file not found"}), 500

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_template = file.read()

        prompt = prompt_template.format(
            record_type=record_type,
            retention_period=retention_period,
            risk_level=risk_level
        )

        # -------------------------------
        # Call AI
        # -------------------------------
        groq_client = GroqClient()
        ai_response = groq_client.generate_response(prompt)

        if not ai_response.get("success"):
            return jsonify({
                "description": "AI service unavailable",
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat(),
                "is_fallback": True
            }), 200

        raw_text = ai_response.get("data", "").strip()

        # Debug (optional but useful)
        print("AI RESPONSE:", raw_text)

        # -------------------------------
        # Clean AI response
        # -------------------------------
        cleaned = re.sub(r"```json|```", "", raw_text).strip()

        # -------------------------------
        # Safe JSON parsing
        # -------------------------------
        try:
            parsed = json.loads(cleaned)
        except Exception as parse_error:
            print("PARSE ERROR:", str(parse_error))

            return jsonify({
                "description": "AI returned invalid JSON",
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat(),
                "is_fallback": True
            }), 200   # changed from 500 → safe fallback

        # -------------------------------
        # Final response
        # -------------------------------
        return jsonify({
            "description": parsed.get("description"),
            "recommendations": parsed.get("recommendations", []),
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": False
        }), 200

    except Exception as e:
        print("ERROR:", str(e))

        return jsonify({
            "description": "Unexpected error occurred",
            "recommendations": [],
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }), 500