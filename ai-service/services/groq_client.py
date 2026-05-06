import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


load_dotenv()


class GroqClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "500"))

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def load_prompt(self, name: str) -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / f"{name}_prompt.txt"
        return prompt_path.read_text(encoding="utf-8").strip()

    def generate(self, prompt_name: str, payload: dict[str, Any]) -> str | None:
        if not self.is_configured():
            return None

        try:
            from groq import Groq
        except Exception:
            return None

        prompt = self.load_prompt(prompt_name)
        user_message = json.dumps(payload, ensure_ascii=False)
        client = Groq(api_key=self.api_key)

        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message},
                    ],
                )
                return response.choices[0].message.content.strip()
            except Exception:
                if attempt == 2:
                    return None
                time.sleep(0.4 * (attempt + 1))

        return None


groq_client = GroqClient()
