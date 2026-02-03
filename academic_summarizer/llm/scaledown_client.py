import requests
import os

class ScaleDownLLM:
    def __init__(self, model="gpt-4o-mini"):
        self.api_key = os.getenv("SCALEDOWN_API_KEY")
        self.base_url = os.getenv("SCALEDOWN_BASE_URL")
        self.model = model

    def generate(self, prompt, temperature=0):
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
