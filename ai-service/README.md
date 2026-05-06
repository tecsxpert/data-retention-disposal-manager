# Data Retention and Disposal Manager - AI Service

Flask microservice for Tool-51. It generates retention descriptions, disposal recommendations, and structured reports for data lifecycle records.

## Features

- `POST /describe` returns a concise retention sentence.
- `POST /recommend` returns exactly three recommendation objects.
- `POST /generate-report` returns a structured report.
- `GET /health` reports service status, model name, cache type, uptime, and optional knowledge-base preload status.
- Groq API integration with 3 retries and deterministic fallback output.
- SHA256 response cache with a 15 minute default TTL.
- Input validation, basic prompt-injection rejection, and security headers.
- Rate limiting at 30 requests/minute when `flask-limiter` is installed.

## Setup

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

The service runs on:

```text
http://localhost:5000
```

## Environment Variables

| Name | Default | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | empty | Enables live Groq responses. Without it, fallback output is used. |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Chat model name. |
| `GROQ_TEMPERATURE` | `0.3` | Lower value for factual policy text. |
| `GROQ_MAX_TOKENS` | `500` | Maximum tokens for AI output. |
| `FLASK_HOST` | `0.0.0.0` | Flask bind host. |
| `FLASK_PORT` | `5000` | Flask port. |
| `CACHE_TYPE` | `SimpleCache` | Flask-Caching backend. |
| `CACHE_DEFAULT_TIMEOUT` | `900` | Cache TTL in seconds. |
| `RATE_LIMIT` | `30 per minute` | Default per-IP request limit. |
| `ENABLE_KNOWLEDGE_BASE` | `false` | Optional sentence-transformer preload switch. |

## API Reference

### Health

```http
GET /health
```

### Describe

```http
POST /describe
Content-Type: application/json
```

```json
{
  "recordType": "Employee Data",
  "retentionPeriod": "5 years",
  "riskLevel": "High"
}
```

Response:

```json
{
  "description": "Employee Data with High risk should be securely retained for 5 years before approved disposal.",
  "generated_at": "2026-05-06T10:00:00.000000",
  "is_fallback": true
}
```

### Recommend

```http
POST /recommend
Content-Type: application/json
```

Response:

```json
[
  {
    "action_type": "Encrypt",
    "description": "Encrypt Employee Data to protect sensitive information.",
    "priority": "High"
  },
  {
    "action_type": "Strict Access Control",
    "description": "Limit access to authorized personnel only.",
    "priority": "High"
  },
  {
    "action_type": "Secure Deletion",
    "description": "Ensure secure deletion after 5 years.",
    "priority": "High"
  }
]
```

### Generate Report

```http
POST /generate-report
Content-Type: application/json
```

Response:

```json
{
  "report": {
    "title": "Employee Data Retention Report",
    "summary": "Employee Data requires handling controls because it is classified as High risk.",
    "overview": "Employee Data should be retained for 5 years, protected during the retention window, and disposed through an approved secure process.",
    "key_items": [
      "Record Type: Employee Data",
      "Retention Period: 5 years",
      "Risk Level: High"
    ],
    "recommendations": [
      "Encrypt Employee Data to protect sensitive information.",
      "Limit access to authorized personnel only.",
      "Ensure secure deletion after 5 years."
    ]
  },
  "generated_at": "2026-05-06T10:00:00.000000",
  "is_fallback": true
}
```

## Docker

```bash
docker build -t tool51-ai-service .
docker run --env-file .env -p 5000:5000 tool51-ai-service
```

## Tests

```bash
pytest
```

The tests use fallback behavior, so they do not require a live Groq API key.
