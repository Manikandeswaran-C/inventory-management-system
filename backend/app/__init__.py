"""
Inventory Management System - Application Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import items


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create DB tables (Alembic handles migrations; this is fallback)
    Base.metadata.create_all(bind=engine)

    application = FastAPI(
        title="Inventory Management System",
        description=(
            "A warehouse inventory manager with stock control.\n\n"
            "## Features\n"
            "- Add items to inventory\n"
            "- Update stock quantities\n"
            "- Automatic low-stock alerts\n"
            "- Prevents negative stock\n"
        ),
        version="1.0.0",
        contact={
            "name": "Inventory Management API",
            "email": "support@inventory.local",
        },
        license_info={
            "name": "MIT",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS - allow React frontend
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    application.include_router(items.router, prefix="/items", tags=["Items"])

    @application.get("/", tags=["Health"])
    def root():
        """Health check endpoint."""
        return {
            "status": "online",
            "service": "Inventory Management System",
            "version": "1.0.0",
            "docs": "/docs",
        }

    @application.get("/health", tags=["Health"])
    def health():
        """Detailed health check."""
        return {"status": "healthy", "database": "connected"}

    return application
