from langchain_text_splitters import RecursiveCharacterTextSplitter

# Tuned for academic papers: preserve paragraphs, enough overlap to avoid cutting mid-sentence
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 240
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks suitable for RAG. Prefers paragraph boundaries."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
    )
    return splitter.split_text(text)
