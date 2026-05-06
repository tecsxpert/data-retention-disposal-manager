from datetime import datetime

from flask import Blueprint, request

from services.ai_cache import cached_json
from services.groq_client import groq_client
from services.validation import validate_payload


describe_bp = Blueprint("describe", __name__)


@describe_bp.route("/describe", methods=["POST"])
def describe():
    payload, error = validate_payload(request.get_json(silent=True))
    if error:
        return error

    def build_response():
        generated = groq_client.generate("describe", payload)
        is_fallback = generated is None
        description = generated or (
            f"{payload['recordType']} with {payload['riskLevel']} risk should be securely retained for "
            f"{payload['retentionPeriod']} before approved disposal."
        )
        return {
            "description": description,
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": is_fallback,
        }

    return cached_json("describe", payload, build_response)
