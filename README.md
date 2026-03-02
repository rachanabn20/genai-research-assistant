# AI Research Paper Assistant

An AI-powered research paper analysis tool built with FastAPI, OpenAI GPT-4o-mini,
and RAG (Retrieval Augmented Generation).

Upload research papers as PDFs and get instant AI-powered summaries, Q&A,
key findings extraction, and methodology analysis — all grounded in the actual
paper content to minimize hallucination.

## Architecture

Client -> FastAPI -> RAG Engine -> ChromaDB (Vector Search) -> OpenAI LLM -> Response


### Components

- **FastAPI Backend** — Async REST API with auto-generated documentation
- **RAG Pipeline** — Retrieval Augmented Generation for accurate, grounded answers
- **ChromaDB** — Vector database for semantic search over paper content
- **OpenAI GPT-4o-mini** — Cost-efficient LLM for text generation
- **Prompt Engineering** — Production-grade prompts with anti-hallucination guardrails

## Features

- PDF upload and text extraction (up to 10MB)
- Question answering grounded in paper content
- Automatic paper summarization
- Key findings extraction
- Methodology analysis
- API key authentication
- Rate limiting
- Prompt injection defense
- Structured logging with token usage tracking
- Docker containerization
- CI/CD with GitHub Actions
- Cloud deployment on Render

## Quick Start

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key with credit

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/genai-research-assistant.git
cd genai-research-assistant
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY and API_KEY_SECRET
uvicorn app.main:app --reload --port 8000


Open http://localhost:8000/docs for interactive API documentation.
