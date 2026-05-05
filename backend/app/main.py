from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.error_handler import register_error_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"], # React frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handlers (must be registered before routers) ────────────────
register_error_handlers(app)

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

@app.get("/")
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

# Import-guarded router mounts
try:
    from app.api.routers import auth
    app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
except ImportError:
    pass

try:
    from app.api.routers import lawyers
    app.include_router(lawyers.router, prefix=f"{settings.API_V1_STR}/lawyers", tags=["lawyers"])
except ImportError:
    pass

try:
    from app.api.routers import admin
    app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
except ImportError:
    pass

try:
    from app.api.routers import chat
    app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
except ImportError:
    pass

try:
    from app.api.routers import ai
    app.include_router(ai.router, prefix=f"{settings.API_V1_STR}", tags=["ai"])
except ImportError as e:
    print("Failed to import AI router:", e)

try:
    from app.api.routers import analyze
    app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}", tags=["analyze"])
except ImportError as e:
    print("Failed to import Analyze router:", e)

try:
    from app.api.routers import cases
    app.include_router(cases.router, prefix=f"{settings.API_V1_STR}/cases", tags=["cases"])
except ImportError as e:
    print("Failed to import Cases router:", e)

try:
    from app.api.routers import messaging
    app.include_router(messaging.router, prefix=f"{settings.API_V1_STR}/messages", tags=["messaging"])
except ImportError as e:
    print("Failed to import Messaging router:", e)

try:
    from app.api.routers import profile
    app.include_router(profile.router, prefix=f"{settings.API_V1_STR}/profile", tags=["profile"])
except ImportError as e:
    print("Failed to import Profile router:", e)

try:
    from app.api.routers import consultations
    app.include_router(consultations.router, prefix=f"{settings.API_V1_STR}/consultations", tags=["consultations"])
except ImportError as e:
    print("Failed to import Consultations router:", e)

try:
    from app.api.routers import archive
    app.include_router(archive.router, prefix=f"{settings.API_V1_STR}/archive", tags=["archive"])
except ImportError as e:
    print("Failed to import Archive router:", e)
