import html
import re
from typing import Any


REQUIRED_FIELDS = ("recordType", "retentionPeriod", "riskLevel")
ALLOWED_RISK_LEVELS = {"High", "Medium", "Low"}
INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*prompt",
    r"<\s*script",
    r"drop\s+table",
    r"delete\s+from",
    r"--",
)


def validate_payload(data: Any) -> tuple[dict[str, str] | None, tuple[dict[str, str], int] | None]:
    if not isinstance(data, dict) or not data:
        return None, ({"error": "Request body is required"}, 400)

    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        return None, ({"error": "recordType, retentionPeriod and riskLevel are required"}, 400)

    cleaned = {field: html.escape(str(data[field]).strip(), quote=True) for field in REQUIRED_FIELDS}
    if cleaned["riskLevel"] not in ALLOWED_RISK_LEVELS:
        return None, ({"error": "riskLevel must be High, Medium or Low"}, 400)

    combined = " ".join(cleaned.values()).lower()
    if any(re.search(pattern, combined, flags=re.IGNORECASE) for pattern in INJECTION_PATTERNS):
        return None, ({"error": "Input failed security validation"}, 400)

    return cleaned, None
