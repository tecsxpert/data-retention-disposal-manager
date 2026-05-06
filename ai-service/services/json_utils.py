import json
import re
from typing import Any


def parse_json_response(text: str) -> Any:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start_indexes = [index for index in (cleaned.find("{"), cleaned.find("[")) if index != -1]
    if not start_indexes:
        raise json.JSONDecodeError("No JSON object or array found", cleaned, 0)

    start = min(start_indexes)
    end = max(cleaned.rfind("}"), cleaned.rfind("]"))
    if end <= start:
        raise json.JSONDecodeError("No complete JSON object or array found", cleaned, start)

    return json.loads(cleaned[start : end + 1])
