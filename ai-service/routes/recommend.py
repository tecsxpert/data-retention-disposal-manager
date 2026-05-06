from flask import Blueprint, request

from services.ai_cache import cached_json
from services.groq_client import groq_client
from services.json_utils import parse_json_response
from services.validation import validate_payload


recommend_bp = Blueprint("recommend", __name__)


def fallback_recommendations(payload):
    record_type = payload["recordType"]
    retention_period = payload["retentionPeriod"]
    risk_level = payload["riskLevel"]

    if risk_level == "High":
        return [
            {
                "action_type": "Encrypt",
                "description": f"Encrypt {record_type} to protect sensitive information.",
                "priority": "High",
            },
            {
                "action_type": "Strict Access Control",
                "description": "Limit access to authorized personnel only.",
                "priority": "High",
            },
            {
                "action_type": "Secure Deletion",
                "description": f"Ensure secure deletion after {retention_period}.",
                "priority": "High",
            },
        ]

    if risk_level == "Medium":
        return [
            {
                "action_type": "Archive",
                "description": f"Archive {record_type} securely during retention period.",
                "priority": "Medium",
            },
            {
                "action_type": "Periodic Review",
                "description": "Review data regularly for compliance.",
                "priority": "Medium",
            },
            {
                "action_type": "Delete",
                "description": f"Delete data after {retention_period}.",
                "priority": "Low",
            },
        ]

    return [
        {
            "action_type": "Store",
            "description": f"Store {record_type} with basic protection.",
            "priority": "Low",
        },
        {
            "action_type": "Minimal Monitoring",
            "description": "Monitor data usage occasionally.",
            "priority": "Low",
        },
        {
            "action_type": "Delete",
            "description": f"Delete data after {retention_period}.",
            "priority": "Low",
        },
    ]


def is_valid_recommendation_list(value, payload):
    retention_period = payload["retentionPeriod"].lower()
    if not isinstance(value, list) or len(value) != 3:
        return False

    for item in value:
        if not isinstance(item, dict):
            return False
        if not {"action_type", "description", "priority"} <= set(item):
            return False
        if item["action_type"] not in {"Archive", "Review", "Delete", "Encrypt", "Strict Access Control", "Secure Deletion", "Store", "Minimal Monitoring", "Periodic Review"}:
            return False
        if item["priority"] not in {"High", "Medium", "Low"}:
            return False
        if "delete" in item["description"].lower() and retention_period not in item["description"].lower():
            return False

    return True


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    payload, error = validate_payload(request.get_json(silent=True))
    if error:
        return error

    def build_response():
        generated = groq_client.generate("recommend", payload)
        if generated:
            try:
                parsed = parse_json_response(generated)
                if is_valid_recommendation_list(parsed, payload):
                    return parsed
            except ValueError:
                pass
        return fallback_recommendations(payload)

    return cached_json("recommend", payload, build_response)
