"""
API Routes
------------
Defines all HTTP endpoints for the Research Paper Assistant.

POST /api/v1/papers/upload     Upload a research paper PDF
POST /api/v1/papers/question   Ask a question about a paper
POST /api/v1/papers/analyze    Get analysis (summary, findings, methodology)
GET  /api/v1/health            Health check
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request

from app.models.schemas import (
    QuestionRequest,
    AnalysisRequest,
    UploadResponse,
    AnswerResponse,
    AnalysisResponse,
    HealthResponse,
)
from app.services.rag_service import RAGService
from app.dependencies import get_rag
from core.config import get_settings
from core.security import verify_api_key, sanitize_input, limiter
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Research Paper Assistant"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
)
async def health_check():
    """
    Returns the application status. Deployment platforms and load
    balancers call this endpoint to verify the application is alive.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.post(
    "/papers/upload",
    response_model=UploadResponse,
    summary="Upload Research Paper",
)
@limiter.limit("5/minute")
async def upload_paper(
    request: Request,
    file: UploadFile = File(..., description="PDF file to upload"),
    api_key: str = Depends(verify_api_key),
    rag_service: RAGService = Depends(get_rag),
):
    """
    Upload a PDF research paper for processing.

    The paper is validated, text is extracted, split into chunks,
    embedded, and stored in the vector database. Returns a paper_id
    that you use for all subsequent queries.
    """
    try:
        content = await file.read()
        result = await rag_service.ingest_paper(
            file_content=content,
            filename=file.filename or "unnamed.pdf",
        )

        return UploadResponse(
            paper_id=result["paper_id"],
            filename=result["filename"],
            pages=result["pages"],
            chunks=result["chunks"],
            message=(
                f"Paper processed successfully. "
                f"{result['chunks']} chunks indexed. "
                f"Use paper_id '{result['paper_id']}' for queries."
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process paper: {str(e)}")


@router.post(
    "/papers/question",
    response_model=AnswerResponse,
    summary="Ask Question About Paper",
)
@limiter.limit("20/minute")
async def ask_question(
    request: Request,
    question_request: QuestionRequest,
    api_key: str = Depends(verify_api_key),
    rag_service: RAGService = Depends(get_rag),
):
    """
    Ask a specific question about an uploaded research paper.
    The system retrieves relevant sections and generates an answer
    grounded in the actual paper content.
    """
    try:
        clean_question = sanitize_input(question_request.question)
        result = await rag_service.ask_question(
            paper_id=question_request.paper_id,
            question=clean_question,
        )
        return AnswerResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("question_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/papers/analyze",
    response_model=AnalysisResponse,
    summary="Analyze Paper",
)
@limiter.limit("10/minute")
async def analyze_paper(
    request: Request,
    analysis_request: AnalysisRequest,
    api_key: str = Depends(verify_api_key),
    rag_service: RAGService = Depends(get_rag),
):
    """
    Get AI-generated analysis of a paper.
    Available types: summarize, key_findings, methodology.
    """
    try:
        result = await rag_service.analyze_paper(
            paper_id=analysis_request.paper_id,
            analysis_type=analysis_request.analysis_type.value,
        )
        return AnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))