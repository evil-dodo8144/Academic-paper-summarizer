import os
import time

import requests

# api.scaledown.ai does not resolve; use .xyz for ScaleDown chat
_DEFAULT_BASE_URL = "https://api.scaledown.xyz/v1"
_MAX_RETRIES_429 = 4
_INITIAL_BACKOFF = 2.0


class ScaleDownLLM:
    def __init__(self, model="gpt-4o-mini"):
        self.api_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()
        raw_url = (os.getenv("SCALEDOWN_BASE_URL") or "").strip()
        # api.scaledown.ai does not resolve; use .xyz host instead
        if raw_url and "api.scaledown.ai" not in raw_url:
            self.base_url = raw_url
        else:
            self.base_url = _DEFAULT_BASE_URL
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
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }

        def do_request(use_x_key: bool):
            headers = {"Content-Type": "application/json"}
            if use_x_key:
                headers["x-api-key"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
            return requests.post(url, headers=headers, json=payload)

        response = do_request(use_x_api_key)
        # 403 often means wrong auth style; retry with the other (Bearer vs x-api-key)
        if response.status_code == 403:
            response = do_request(not use_x_api_key)
        if response.status_code == 401:
            raise ValueError(
                "401 Unauthorized: invalid or wrong API key. "
                "For api.openai.com use an OpenAI key from https://platform.openai.com/api-keys (starts with sk-). "
                "Set it in .env as SCALEDOWN_API_KEY=sk-your-key"
            ) from None
        # 429 Too Many Requests: retry with backoff (rate limit)
        if response.status_code == 429:
            for attempt in range(_MAX_RETRIES_429):
                try:
                    wait = int(response.headers.get("Retry-After", _INITIAL_BACKOFF * (2**attempt)))
                except (TypeError, ValueError):
                    wait = _INITIAL_BACKOFF * (2**attempt)
                wait = min(wait, 60)
                time.sleep(wait)
                response = do_request(use_x_api_key)
                if response.status_code != 429:
                    break
            if response.status_code == 429:
                raise ValueError(
                    "429 Too Many Requests: OpenAI rate limit hit. Wait a minute and try again, "
                    "or check your usage at https://platform.openai.com/usage."
                ) from None
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
