# Academic Paper Summarizer

A research paper summarization tool that uses **compression** to handle lengthy academic papers while **preserving technical accuracy** and **reducing processing time**.

## What it does

- **Upload a PDF** (research paper, article) and get a concise, accurate summary.
- **RAG (Retrieval-Augmented Generation)**: chunks the document, optionally compresses chunks, embeds them, and retrieves the most relevant parts for your query before generating the summary.
- **Compression**: long documents are chunked and can be compressed (via ScaleDown API or LLM) so that embedding and retrieval stay fast and within context limits.
- **Technical accuracy**: the summarization prompt instructs the model to preserve key terms, methods, and findings.

## Pipeline

1. **Load PDF** → extract text (PyMuPDF).
2. **Chunk** → split into overlapping segments (paragraph-aware, tuned for academic text).
3. **Compress** (optional) → shorten chunks via ScaleDown compress API or an LLM to reduce tokens while keeping meaning.
4. **Embed** → compute embeddings (e.g. sentence-transformers).
5. **Vector store** → FAISS index over compressed chunks.
6. **Retrieve** → fetch top-k chunks most relevant to the user’s query.
7. **Summarize** → LLM generates a summary from the retrieved context, with instructions to preserve technical accuracy.

## Setup

### 1. Clone and enter the app directory

```bash
cd academic_summarizer
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Environment variables

Copy the example env file and edit `.env`:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

### 4. For installing sentence transformer run: 
        
`pip install sentence-transformers`

In `.env` set:

- **`SCALEDOWN_BASE_URL`** – For **chat** (summarization), use an OpenAI-compatible endpoint, e.g. `https://api.openai.com/v1`.
- **`SCALEDOWN_API_KEY`** – Your API key. For OpenAI chat use a key from [platform.openai.com](https://platform.openai.com/api-keys) (starts with `sk-`).
- **`SCALEDOWN_USE_X_API_KEY`** – Set to `0` or leave unset for OpenAI (Bearer token).

Optional (for **chunk compression** via ScaleDown):

- **`SCALEDOWN_COMPRESS_URL`** – e.g. `https://api.scaledown.xyz/compress/raw/`
- Use the same or a separate key; ScaleDown compress uses the `x-api-key` header.

### 4. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

- **Web UI**: open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) → “Summarize a paper” → upload PDF and optional query.
- **API**: `POST /api/summarize/` with form-data `file` (PDF) and optional `query`.

## API

- **GET /** – Home page.
- **GET /summarize/** – Summarization form.
- **POST /summarize/** – Submit PDF and optional query (web form).
- **GET /api/** – API root and list of endpoints.
- **POST /api/summarize/** – `file` (PDF), `query` (optional). Returns `{"summary": "..."}`.

## Project structure

```
academic_summarizer/
│
├── manage.py
├── requirements.txt
├── .env.local                       # Your keys
│
├── academic_summarizer/             # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── api/                               # REST endpoints
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│
├── rag/                               # PDF → chunk → compress → embed → retrieve → summarize
│   ├── pdf_loader.py
│   ├── chunker.py
│   ├── compressor.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── summarize.py
├── templates/
│   ├── summarize.html
│   └── home.html
│
└── llm/                                # Chat (summarization) and compress clients
    ├── scaledown_client.py
    └── scaledown_compress.py

```

## License

See [LICENSE](LICENSE).
