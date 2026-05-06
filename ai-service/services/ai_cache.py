import hashlib
import json
from typing import Any, Callable

from extensions import cache


def cached_json(prefix: str, payload: dict[str, Any], factory: Callable[[], Any], timeout: int = 900) -> Any:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    key = f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"
    cached = cache.get(key)
    if cached is not None:
        return cached

    value = factory()
    if isinstance(value, dict) and value.get("is_fallback") is True:
        return value

    cache.set(key, value, timeout=timeout)
    return value
