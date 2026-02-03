"""ScaleDown Compress API client: https://api.scaledown.xyz/compress/raw/ with x-api-key."""

import os
import requests


def compress_text(text: str, context: str = "") -> str:
    """
    Compress text via ScaleDown API. Uses SCALEDOWN_COMPRESS_URL and SCALEDOWN_API_KEY from env.
    Payload format: context, prompt, scaledown.rate (see ScaleDown docs).
    """
    url = (os.getenv("SCALEDOWN_COMPRESS_URL") or "https://api.scaledown.xyz/compress/raw/").strip().rstrip("/") + "/"
    api_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()

    if not api_key:
        raise ValueError(
            "SCALEDOWN_API_KEY is not set. Add it to your .env file for the compress API."
        )

    # Documented payload: context, prompt, scaledown.rate
    payload = {
        "context": context or "Academic paper excerpt.",
        "prompt": text,
        "scaledown": {"rate": "auto"},
    }

    response = requests.post(
        url,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content_type = (response.headers.get("Content-Type") or "").lower()
    if "application/json" in content_type:
        data = response.json()
        if isinstance(data, str):
            return data
        return (
            data.get("compressed")
            or data.get("prompt")
            or data.get("result")
            or data.get("text")
            or str(data)
        )
    return response.text
