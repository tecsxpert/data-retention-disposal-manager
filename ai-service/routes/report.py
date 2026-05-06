from datetime import datetime

from flask import Blueprint, request

from routes.recommend import fallback_recommendations
from services.ai_cache import cached_json
from services.groq_client import groq_client
from services.json_utils import parse_json_response
from services.validation import validate_payload


report_bp = Blueprint("report", __name__)


def fallback_report(payload):
    record_type = payload["recordType"]
    retention_period = payload["retentionPeriod"]
    risk_level = payload["riskLevel"]

    return {
        "title": f"{record_type} Retention Report",
        "summary": f"{record_type} requires handling controls because it is classified as {risk_level} risk.",
        "overview": (
            f"{record_type} should be retained for {retention_period}, protected during the retention window, "
            "and disposed through an approved secure process."
        ),
        "key_items": [
            f"Record Type: {record_type}",
            f"Retention Period: {retention_period}",
            f"Risk Level: {risk_level}",
        ],
        "recommendations": [item["description"] for item in fallback_recommendations(payload)],
    }


def is_valid_report(value):
    required = {"title", "summary", "overview", "key_items", "recommendations"}
    return (
        isinstance(value, dict)
        and required <= set(value)
        and isinstance(value["key_items"], list)
        and isinstance(value["recommendations"], list)
    )


@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    payload, error = validate_payload(request.get_json(silent=True))
    if error:
        return error

    def build_response():
        generated = groq_client.generate("report", payload)
        if generated:
            try:
                parsed = parse_json_response(generated)
                if is_valid_report(parsed):
                    return {
                        "report": parsed,
                        "generated_at": datetime.utcnow().isoformat(),
                        "is_fallback": False,
                    }
            except ValueError:
                pass
        return {
            "report": fallback_report(payload),
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True,
        }

    return cached_json("report", payload, build_response)
