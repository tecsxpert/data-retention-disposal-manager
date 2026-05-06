import os
import time

from flask import Flask, g
from dotenv import load_dotenv

from extensions import cache


load_dotenv()

app = Flask(__name__)
START_TIME = time.time()

app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "SimpleCache")
app.config["CACHE_DEFAULT_TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "900"))
app.config["JSON_SORT_KEYS"] = False

cache.init_app(app)
app.config["RESPONSE_COUNT"] = 0
app.config["TOTAL_RESPONSE_TIME_MS"] = 0.0

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[os.getenv("RATE_LIMIT", "30 per minute")],
        storage_uri=os.getenv("LIMITER_STORAGE_URI", "memory://"),
    )
except Exception as exc:
    limiter = None
    app.logger.warning("Rate limiter disabled: %s", exc)

try:
    from services.knowledge_base import preload_knowledge_base

    KNOWLEDGE_STATUS = preload_knowledge_base()
except Exception as exc:
    KNOWLEDGE_STATUS = {"enabled": False, "status": "unavailable", "detail": str(exc)}

from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)


@app.route("/health")
def health():
    response_count = app.config.get("RESPONSE_COUNT", 0)
    total_response_time = app.config.get("TOTAL_RESPONSE_TIME_MS", 0.0)
    avg_response_time = round(total_response_time / response_count, 2) if response_count else 0

    return {
        "status": "working",
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "cache": app.config["CACHE_TYPE"],
        "knowledge_base": KNOWLEDGE_STATUS,
        "avg_response_time_ms": avg_response_time,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.before_request
def start_timer():
    g.request_started_at = time.perf_counter()


@app.after_request
def add_security_headers(response):
    started_at = getattr(g, "request_started_at", None)
    if started_at is not None:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        app.config["RESPONSE_COUNT"] += 1
        app.config["TOTAL_RESPONSE_TIME_MS"] += elapsed_ms

    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
