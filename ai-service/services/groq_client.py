import requests
import time
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

class GroqClient:

    def __init__(self):
        # Load API key from environment
        self.api_key = os.getenv("GROQ_API_KEY")

        # Check if API key exists
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")

        # API endpoint
        self.url = "https://api.groq.com/openai/v1/chat/completions"

        # Headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_response(self, prompt, max_retries=3):

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    # Safe extraction (prevents crash if structure changes)
                    ai_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                    return {
                        "success": True,
                        "data": ai_text,
                        "is_fallback": False
                    }

                else:
                    logging.error(f"Error: {response.text}")

            except Exception as e:
                logging.error(f"Exception: {str(e)}")

            time.sleep(2 ** attempt)

        return {
            "success": False,
            "data": "AI unavailable",
            "is_fallback": True
        }