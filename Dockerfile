FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENAI_MODEL=llama-3.1-8b-instant \
    OPENAI_EMBEDDING_MODEL=local \
    APP_NAME=AI_Research_Paper_Assistant \
    APP_VERSION=1.0.0 \
    APP_ENV=production \
    DEBUG=false \
    ALLOWED_ORIGINS=* \
    RATE_LIMIT_PER_MINUTE=20 \
    CHUNK_SIZE=1000 \
    CHUNK_OVERLAP=200 \
    MAX_CONTEXT_CHUNKS=5 \
    MAX_INPUT_TOKENS=4000 \
    MAX_OUTPUT_TOKENS=2000 \
    MAX_FILE_SIZE_MB=10 \
    UPLOAD_DIR=uploads

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]