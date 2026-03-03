# AI Research Paper Assistant

An AI-powered tool that analyzes research papers using RAG (Retrieval Augmented Generation). Upload a PDF, ask questions, and get answers grounded in actual paper content.

**Live Demo:** (https://rachanaBN-research-paper-assistant.hf.space/app)

**GitHub:** (https://github.com/rachanabn20/genai-research-assistant)

---

## Architecture
Browser --> FastAPI API --> PDF Processing --> Text Chunking
|
v
Local Embeddings (sentence-transformers)
|
v
ChromaDB (Vector Search)
|
v
Groq LLM (LLaMA 3.1) --> AI Response


## Features

- Upload PDF research papers (up to 10MB)
- Ask questions with answers grounded in paper content
- Generate structured summaries
- Extract key findings
- Analyze methodology
- API key authentication and rate limiting
- Prompt injection defense
- Docker and CI/CD support

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) + Python 3.12 |
| LLM | [Groq](https://groq.com/) (LLaMA 3.1 8B) — free tier |
| Embeddings | [sentence-transformers](https://www.sbert.net/) — runs locally |
| Vector DB | [ChromaDB](https://www.trychroma.com/) — runs locally |
| Text Splitting | [LangChain](https://www.langchain.com/) |
| Deployment | [Hugging Face Spaces](https://huggingface.co/spaces) |
| CI/CD | [GitHub Actions](https://github.com/features/actions) |

## Quick Start
```bash
git clone https://github.com/rachanabn20/genai-research-assistant.git
cd genai-research-assistant
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env: add your GROQ_API_KEY and set API_KEY_SECRET
python -m uvicorn app.main:app --reload --port 8000
# Edit .env: add your GROQ_API_KEY and set API_KEY_SECRET
python -m uvicorn app.main:app --reload --port 8000



