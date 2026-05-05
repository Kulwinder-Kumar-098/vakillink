from fastapi import APIRouter
from ai.models.schemas import HealthResponse
from ai.core.embedder import embedder
from ai.core.qdrant_client import get_qdrant_client
from ai.core.config import settings

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    Railway and Render ping this to confirm the service is live.
    """
    model_loaded = embedder._model is not None

    qdrant_ok = False
    try:
        client = get_qdrant_client()
        # Lightweight check: just list collections, don't do a search
        client.get_collections()
        qdrant_ok = True
    except Exception:
        qdrant_ok = False

    return HealthResponse(
        status="ok" if (model_loaded and qdrant_ok) else "degraded",
        model_loaded=model_loaded,
        qdrant_connected=qdrant_ok,
        version="1.0.0",
    )
