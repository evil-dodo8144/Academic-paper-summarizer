from langchain_community.vectorstores import FAISS

def build_vectorstore(texts, embeddings):
    return FAISS.from_texts(texts, embeddings)
