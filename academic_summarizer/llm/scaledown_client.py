import os
import time

import requests

# api.scaledown.ai does not resolve; use .xyz for ScaleDown chat
_DEFAULT_BASE_URL = "https://api.scaledown.xyz/v1"
_MAX_RETRIES_429 = 4
_INITIAL_BACKOFF = 2.0


class ScaleDownLLM:
    def __init__(self, model="gpt-3.5-mini"):
        # Use ScaleDown if configured, otherwise fall back to Groq.
        scaledown_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()
        groq_key = (os.getenv("GROQ_API_KEY") or "").strip()

        if scaledown_key:
            self.api_key = scaledown_key
            raw_url = (os.getenv("SCALEDOWN_BASE_URL") or "").strip()
            # api.scaledown.ai does not resolve; use .xyz host instead
            if raw_url and "api.scaledown.ai" not in raw_url:
                self.base_url = raw_url
            else:
                self.base_url = _DEFAULT_BASE_URL
            self.provider = "scaledown"
        elif groq_key:
            # Groq exposes an OpenAI-compatible API surface at this base URL.
            self.api_key = groq_key
            self.base_url = (os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1").strip()
            self.provider = "groq"
        else:
            self.api_key = ""
            self.base_url = ""
            self.provider = "unset"

        self.model = model

    def generate(self, prompt, temperature=0):
        if not self.base_url or not self.base_url.strip():
            if getattr(self, "provider", "") == "groq":
                raise ValueError(
                    "GROQ_BASE_URL is not set. "
                    "Add it to your .env file (e.g. GROQ_BASE_URL=https://api.groq.com/openai/v1)."
                )
            raise ValueError(
                "SCALEDOWN_BASE_URL is not set. "
                "Add it to your .env file (e.g. SCALEDOWN_BASE_URL=https://api.scaledown.xyz/v1)."
            )
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "No API key configured. "
                "Set SCALEDOWN_API_KEY to use ScaleDown, or GROQ_API_KEY to use Groq, in your .env file."
            )
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        use_x_api_key = (
            getattr(self, "provider", "") == "scaledown"
            and os.getenv("SCALEDOWN_USE_X_API_KEY", "").strip().lower() in ("1", "true", "yes")
        )
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
                # headers["Authorization"] = f"Bearer {self.api_key}"
                headers = {
    "Authorization": f"Bearer {self.api_key}",  
    "Content-Type": "application/json"
}

            return requests.post(url, headers=headers, json=payload)

        response = do_request(use_x_api_key)
        # 403 often means wrong auth style; retry with the other (Bearer vs x-api-key)
        if response.status_code == 403:
            response = do_request(not use_x_api_key)
        if response.status_code == 401:
            if getattr(self, "provider", "") == "groq":
                raise ValueError(
                    "401 Unauthorized: invalid or wrong Groq API key. "
                    "Set GROQ_API_KEY in your .env file to a valid Groq key."
                ) from None
            raise ValueError(
                "401 Unauthorized: invalid or wrong ScaleDown API key. "
                "Set SCALEDOWN_API_KEY in your .env file to a valid ScaleDown key."
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
                provider = getattr(self, "provider", "provider")
                raise ValueError(
                    f"429 Too Many Requests: {provider} rate limit hit. Wait a minute and try again."
                ) from None
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
