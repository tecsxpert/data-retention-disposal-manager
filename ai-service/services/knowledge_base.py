import os


DOCUMENTS = [
    "Retention schedules should map record type, legal basis, owner, and disposal date.",
    "High-risk records require encryption, strict access control, audit logging, and verified disposal.",
    "Medium-risk records should be archived securely and reviewed at defined intervals.",
    "Low-risk records still need clear retention dates and deletion confirmation.",
    "Disposal should be irreversible for expired records unless a legal hold is active.",
    "Prompt inputs must avoid personal data and secrets whenever possible.",
    "AI output is advisory and should be reviewed against company policy and applicable law.",
    "Caching repeated AI requests improves response time and reduces external API usage.",
    "Fallback responses keep workflows available during model outages or rate limits.",
    "Health checks should expose service readiness without leaking secrets.",
]


def preload_knowledge_base() -> dict[str, object]:
    if os.getenv("ENABLE_KNOWLEDGE_BASE", "false").lower() != "true":
        return {"enabled": False, "status": "disabled"}

    try:
        from sentence_transformers import SentenceTransformer

        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_name)
        model.encode(DOCUMENTS[:1])
        return {"enabled": True, "status": "ready", "documents": len(DOCUMENTS), "model": model_name}
    except Exception as exc:
        return {"enabled": False, "status": "fallback", "detail": str(exc)}
