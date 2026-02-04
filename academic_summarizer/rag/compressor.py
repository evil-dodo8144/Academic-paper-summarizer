import os

from llm.scaledown_compress import compress_text as scaledown_compress_text


def compress_chunks(chunks):
    """
    Optionally compress chunks before embedding.

    - If SCALEDOWN_COMPRESS_URL is set, use the ScaleDown compress API.
    - Otherwise, return the original chunks without extra LLM calls to avoid
      hammering the chat API (which can easily hit 429 rate limits).
    """
    use_compress_api = (os.getenv("SCALEDOWN_COMPRESS_URL") or "").strip()
    if use_compress_api:
        return [scaledown_compress_text(chunk) for chunk in chunks]
    # No external compress API configured: skip compression to reduce
    # the number of OpenAI chat calls and avoid rate limiting.
    return chunks
