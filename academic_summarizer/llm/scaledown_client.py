import requests
import os

class ScaleDownLLM:
    def __init__(self, model="gpt-4o-mini"):
        self.api_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()
        self.base_url = (os.getenv("SCALEDOWN_BASE_URL") or "").strip()
        self.model = model

    def generate(self, prompt, temperature=0):
        if not self.base_url or not self.base_url.strip():
            raise ValueError(
                "SCALEDOWN_BASE_URL is not set. "
                "Add it to your .env file (e.g. SCALEDOWN_BASE_URL=https://api.openai.com/v1). "
                "Create a .env file in the project root if you don't have one."
            )
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "SCALEDOWN_API_KEY is not set. "
                "Add it to your .env file. Create a .env file in the project root if you don't have one."
            )
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        use_x_api_key = os.getenv("SCALEDOWN_USE_X_API_KEY", "").strip().lower() in ("1", "true", "yes")
        headers = {"Content-Type": "application/json"}
        if use_x_api_key:
            headers["x-api-key"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = requests.post(
            url,
            headers=headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
