import os
import time

import requests

# Default endpoints
_DEFAULT_SCALEDOWN_BASE_URL = "https://api.scaledown.xyz/v1"
_DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"

_MAX_RETRIES_429 = 4
_INITIAL_BACKOFF = 2.0


def _truthy_env(name: str) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return False
    # Be forgiving of inline comments in .env files (e.g. "true  # comment").
    raw = raw.split("#", 1)[0].strip()
    return raw in ("1", "true", "yes", "y", "on")


class ScaleDownLLM:
    """Small OpenAI-compatible chat client.

    Providers:
    - scaledown: SCALEDOWN_API_KEY (+ optional SCALEDOWN_BASE_URL, SCALEDOWN_USE_X_API_KEY)
    - groq: GROQ_API_KEY (+ optional GROQ_BASE_URL)
    - openai: OPENAI_API_KEY (+ optional OPENAI_BASE_URL)

    Selection:
    - If LLM_PROVIDER is set, it forces the provider.
    - Otherwise keeps the previous behavior: ScaleDown -> Groq -> OpenAI.

    Model:
    - If LLM_MODEL is set, it overrides the model.
    - Otherwise uses a provider-appropriate default.
    """

    def __init__(self, model: str | None = None):
        self.provider = "unset"
        self.api_key = ""
        self.base_url = ""

        provider_override = (os.getenv("LLM_PROVIDER") or "").strip().lower()

        scaledown_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()
        groq_key = (os.getenv("GROQ_API_KEY") or "").strip()
        openai_key = (os.getenv("OPENAI_API_KEY") or "").strip()

        if provider_override:
            self._configure_provider(provider_override, scaledown_key, groq_key, openai_key)
        else:
            # Previous behavior (kept for backward compatibility)
            if scaledown_key:
                self._configure_provider("scaledown", scaledown_key, groq_key, openai_key)
            elif groq_key:
                self._configure_provider("groq", scaledown_key, groq_key, openai_key)
            elif openai_key:
                self._configure_provider("openai", scaledown_key, groq_key, openai_key)
            else:
                self.provider = "unset"
                self.api_key = ""
                self.base_url = ""

        env_model = (os.getenv("LLM_MODEL") or "").strip()
        self.model = (model or "").strip() or env_model or self._default_model_for_provider(self.provider)

    def _configure_provider(
        self,
        provider: str,
        scaledown_key: str,
        groq_key: str,
        openai_key: str,
    ) -> None:
        provider = (provider or "").strip().lower()

        if provider == "scaledown":
            if not scaledown_key:
                raise ValueError("LLM_PROVIDER=scaledown but SCALEDOWN_API_KEY is not set.")

            raw_url = (os.getenv("SCALEDOWN_BASE_URL") or "").strip()
            # api.scaledown.ai does not resolve; use .xyz host instead.
            if raw_url and "api.scaledown.ai" not in raw_url:
                base_url = raw_url
            else:
                base_url = _DEFAULT_SCALEDOWN_BASE_URL

            self.provider = "scaledown"
            self.api_key = scaledown_key
            self.base_url = base_url
            return

        if provider == "groq":
            if not groq_key:
                raise ValueError("LLM_PROVIDER=groq but GROQ_API_KEY is not set.")
            self.provider = "groq"
            self.api_key = groq_key
            self.base_url = (os.getenv("GROQ_BASE_URL") or _DEFAULT_GROQ_BASE_URL).strip()
            return

        if provider == "openai":
            if not openai_key:
                raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
            self.provider = "openai"
            self.api_key = openai_key
            self.base_url = (os.getenv("OPENAI_BASE_URL") or _DEFAULT_OPENAI_BASE_URL).strip()
            return

        raise ValueError("Unknown LLM_PROVIDER. Use one of: scaledown, groq, openai.")

    @staticmethod
    def _default_model_for_provider(provider: str) -> str:
        provider = (provider or "").strip().lower()
        if provider == "groq":
            return "llama-3.3-70b-versatile"
        # Works for OpenAI, and many OpenAI-compatible proxies.
        return "gpt-4o-mini"

    def generate(self, prompt: str, temperature: float = 0) -> str:
        if not self.base_url or not self.base_url.strip():
            raise ValueError(
                "No LLM base URL configured. Set LLM_PROVIDER and provider base URL env vars."
            )
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "No API key configured. Set SCALEDOWN_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY."
            )

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        use_x_api_key = self.provider == "scaledown" and _truthy_env("SCALEDOWN_USE_X_API_KEY")

        def do_request(use_x_key: bool):
            headers = {"Content-Type": "application/json"}
            if use_x_key:
                headers["x-api-key"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
            return requests.post(url, headers=headers, json=payload, timeout=60)

        response = do_request(use_x_api_key)

        # ScaleDown 403 often means wrong auth style; retry once with the other.
        if self.provider == "scaledown" and response.status_code == 403:
            response = do_request(not use_x_api_key)

        if response.status_code == 401:
            if self.provider == "groq":
                raise ValueError(
                    "401 Unauthorized: invalid Groq API key. Set GROQ_API_KEY in your .env.local file."
                ) from None
            if self.provider == "openai":
                raise ValueError(
                    "401 Unauthorized: invalid OpenAI API key. Set OPENAI_API_KEY in your .env.local file."
                ) from None
            raise ValueError(
                "401 Unauthorized: invalid ScaleDown API key. Set SCALEDOWN_API_KEY in your .env.local file."
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
                    f"429 Too Many Requests: {self.provider} rate limit hit. Wait a minute and try again."
                ) from None

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
