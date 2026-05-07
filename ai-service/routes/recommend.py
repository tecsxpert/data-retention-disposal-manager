from flask import Blueprint, request, jsonify
from datetime import datetime
from services.groq_client import GroqClient
import os
import json

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():

    # -------------------------------
    # STEP 1: Read request body
    # -------------------------------
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    record_type = data.get("recordType")
    retention_period = data.get("retentionPeriod")
    risk_level = data.get("riskLevel")

    # -------------------------------
    # STEP 2: Validate input
    # -------------------------------
    if not record_type or not retention_period or not risk_level:
        return jsonify({
            "error": "recordType, retentionPeriod and riskLevel are required"
        }), 400

    try:
        # -------------------------------
        # STEP 3: Load prompt template
        # -------------------------------
        base_dir = os.path.dirname(os.path.abspath(__file__))

        prompt_path = os.path.normpath(
            os.path.join(base_dir, "..", "prompts", "recommend_prompt.txt")
        )

        if not os.path.exists(prompt_path):
            return jsonify({
                "error": "Prompt file not found"
            }), 500

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_template = file.read()

        # -------------------------------
        # STEP 4: Inject values into prompt
        # -------------------------------
        prompt = prompt_template.format(
            record_type=record_type,
            retention_period=retention_period,
            risk_level=risk_level
        )

        # -------------------------------
        # STEP 5: Call Groq AI
        # -------------------------------
        groq_client = GroqClient()
        ai_response = groq_client.generate_response(prompt)

        if not ai_response.get("success"):
            return jsonify({
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat(),
                "is_fallback": True
            }), 200

        # -------------------------------
        # STEP 6: Clean AI response
        # -------------------------------
        raw_text = ai_response.get("data", "").strip()

        # Remove wrapping quotes if present
        if raw_text.startswith('"') and raw_text.endswith('"'):
            raw_text = raw_text[1:-1]

        # Remove escape characters
        raw_text = raw_text.replace('\\"', '"')
        raw_text = raw_text.replace('\\n', '')
        raw_text = raw_text.replace('\\t', '')

        # -------------------------------
        # STEP 7: Extract JSON safely
        # -------------------------------
        start = raw_text.find('[')
        end = raw_text.rfind(']') + 1

        if start == -1 or end == -1:
            return jsonify({
                "error": "AI did not return valid JSON array",
                "raw_output": raw_text
            }), 500

        json_text = raw_text[start:end]

        # -------------------------------
        # STEP 8: Convert to Python object
        # -------------------------------
        try:
            recommendations = json.loads(json_text)
        except Exception as e:
            print("JSON ERROR:", str(e))
            return jsonify({
                "error": "AI returned invalid JSON",
                "raw_output": raw_text
            }), 500

        # -------------------------------
        # STEP 9: Enforce valid action types
        # -------------------------------
        valid_actions = {"Retain", "Archive", "Delete"}

        for item in recommendations:
            if item.get("action_type") not in valid_actions:
                item["action_type"] = "Retain"

        # -------------------------------
        # STEP 10: Normalize priority
        # -------------------------------
        priority_map = {
            "Retain": "High",
            "Archive": "Medium",
            "Delete": "Low"
        }

        for item in recommendations:
            item["priority"] = priority_map.get(item["action_type"], "Medium")

        # -------------------------------
        # STEP 11: Final response
        # -------------------------------
        return jsonify({
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": False
        }), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "recommendations": [],
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }), 500
