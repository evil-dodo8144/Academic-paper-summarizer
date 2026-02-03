# Number of retrieved chunks for summary context (more = broader coverage, higher token use)
RETRIEVE_K = 6


def get_retriever(vectorstore):
    return vectorstore.as_retriever(search_kwargs={"k": RETRIEVE_K})
