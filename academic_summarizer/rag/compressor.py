import os

from llm.scaledown_compress import compress_text as scaledown_compress_text
from llm.scaledown_client import ScaleDownLLM


def compress_chunks(chunks):
    use_compress_api = (os.getenv("SCALEDOWN_COMPRESS_URL") or "").strip()
    if use_compress_api:
        return [scaledown_compress_text(chunk) for chunk in chunks]
    llm = ScaleDownLLM()
    compressed = []
    for chunk in chunks:
        prompt = f"""Compress academic text without losing technical meaning.

TEXT:
{chunk}
"""
        compressed.append(llm.generate(prompt))
    return compressed
