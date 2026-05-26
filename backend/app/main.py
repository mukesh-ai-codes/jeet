"""
JEET Backend — FastAPI Entry Point

This file wires everything together and starts the server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, health, students, mentors, admin, courses, parents
# =============================================================
# LIFESPAN: startup & shutdown hooks
# =============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print(f"  🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"     Environment: {settings.APP_ENV}")
    print(f"     Debug mode:  {settings.DEBUG}")
    print(f"     Database:    {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    print("=" * 60)
    yield
    # Shutdown
    print("👋 JEET API shutting down...")


# =============================================================
# APP
# =============================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-driven retention platform for JEE/NEET aspirants",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# =============================================================
# CORS MIDDLEWARE (allows frontend to call us)
# =============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================
# ROUTERS
# =============================================================
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(mentors.router)
app.include_router(admin.router)
app.include_router(courses.router)
app.include_router(parents.router)


# =============================================================
# ROOT
# =============================================================
@app.get("/")
def root():
    return {
        "message": "Welcome to JEET API",
        "docs": "/docs",
        "health": "/api/health",
        "version": settings.APP_VERSION,
    }