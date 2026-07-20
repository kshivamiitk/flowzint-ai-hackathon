from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.dependencies import (
    ai_components,
    engine,
    session_factory,
    settings,
)
from app.api.router import api_router
from app.core.logging import configure_logging
from app.domain.exceptions import DomainError, EntityNotFoundError
from app.infrastructure.db.base import Base
from app.infrastructure.db.seed import seed_database

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await seed_database(session_factory, ai_components.embedding_provider)
    yield
    if ai_components.closable_client:
        await ai_components.closable_client.close()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Incident-aware customer-care platform",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "service": settings.app_name,
        "ai_provider": settings.ai_provider,
        "database": "connected",
        "chatbot": "local" if settings.ai_provider == "local" else "configured",
        "demo_mode": "enabled" if settings.demo_mode else "disabled",
    }


@app.exception_handler(EntityNotFoundError)
async def not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
