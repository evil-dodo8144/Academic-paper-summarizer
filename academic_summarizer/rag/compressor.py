from llm.scaledown_client import ScaleDownLLM

llm = ScaleDownLLM()

def compress_chunks(chunks):
    compressed = []
    for chunk in chunks:
        prompt = f"""
        Compress academic text without losing technical meaning.

        TEXT:
        {chunk}
        """
        compressed.append(llm.generate(prompt))
    return compressed
