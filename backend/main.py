from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.middleware.error_handler import register_error_handlers
from ai.api import retrieval, health as ai_health
from ai.core.embedder import embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy models once at startup (AI components)."""
    logger.info("Starting up VakilLink API...")
    logger.info("Loading AI embedding model...")
    try:
        embedder.load()
        logger.info(f"AI Model ready: {settings.EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to load AI model: {e}")
    yield
    logger.info("Shutting down VakilLink API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handlers
register_error_handlers(app)

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

@app.get("/", tags=["system"])
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

# --- Dashboard Routers ---
try:
    # Temporarily commented out to avoid Supabase key validation errors during RAG testing
    # from app.api.routers import auth, lawyers, admin, chat, ai as dashboard_ai, analyze, cases, messaging, profile, consultations, archive
    # 
    # app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
    # app.include_router(lawyers.router, prefix=f"{settings.API_V1_STR}/lawyers", tags=["lawyers"])
    # app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
    # app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
    # app.include_router(dashboard_ai.router, prefix=f"{settings.API_V1_STR}/dashboard/ai", tags=["dashboard-ai"])
    # app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}/analyze", tags=["analyze"])
    # app.include_router(cases.router, prefix=f"{settings.API_V1_STR}/cases", tags=["cases"])
    # app.include_router(messaging.router, prefix=f"{settings.API_V1_STR}/messages", tags=["messaging"])
    # app.include_router(profile.router, prefix=f"{settings.API_V1_STR}/profile", tags=["profile"])
    # app.include_router(consultations.router, prefix=f"{settings.API_V1_STR}/consultations", tags=["consultations"])
    # app.include_router(archive.router, prefix=f"{settings.API_V1_STR}/archive", tags=["archive"])
    
    # --- RAG API Routers ---
    from api.routes import router as rag_router
    app.include_router(rag_router, prefix=f"{settings.API_V1_STR}/ai", tags=["rag-pipeline"])
except ImportError as e:
    logger.error(f"Failed to load dashboard routers: {e}")

# --- AI (RAG) Routers ---
app.include_router(ai_health.router, prefix="/ai/health", tags=["ai-health"])
# app.include_router(retrieval.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai-retrieval"])
