"""ScaleDown Compress API client: https://api.scaledown.xyz/compress/raw/ with x-api-key."""

import os
import requests


def compress_text(text: str) -> str:
    """
    Compress text via ScaleDown API. Uses SCALEDOWN_COMPRESS_URL and SCALEDOWN_API_KEY from env.
    """
    url = (os.getenv("SCALEDOWN_COMPRESS_URL") or "https://api.scaledown.xyz/compress/raw/").strip().rstrip("/") + "/"
    api_key = (os.getenv("SCALEDOWN_API_KEY") or "").strip()

    if not api_key:
        raise ValueError(
            "SCALEDOWN_API_KEY is not set. Add it to your .env file for the compress API."
        )

    response = requests.post(
        url,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={"text": text},
        timeout=60,
    )
    response.raise_for_status()
    content_type = (response.headers.get("Content-Type") or "").lower()
    if "application/json" in content_type:
        data = response.json()
        if isinstance(data, str):
            return data
        return data.get("compressed") or data.get("result") or data.get("text") or str(data)
    return response.text
