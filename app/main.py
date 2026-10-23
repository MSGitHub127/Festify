"""FastAPI Application Factory with defense-in-depth security headers, CORS, GZip, and static UI mounting."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import init_db
from app.routers import budget, compare, events, ideas, session, timeline, vendors

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("festify")


def create_app() -> FastAPI:
    settings = get_settings()

    if settings.environment == "production" and settings.secret_key == "dev-only-insecure-secret-change-me":
        raise RuntimeError("Refusing to start in production with default secret key. Set FESTIFY_SECRET_KEY.")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        logger.info("Festify database initialized successfully.")
        yield

    app = FastAPI(
        title=settings.app_name,
        description="Context-aware planning assistant for weddings, birthdays, and community events with budgets, timelines, and vendor checklists.",
        version=settings.version,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=500)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' data:; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' http://localhost:8000 https:; "
            "frame-ancestors 'self' *;"
        )
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path == "/" or request.url.path.endswith((".js", ".css", ".svg", ".png", ".ico")):
            response.headers["Cache-Control"] = "public, max-age=3600"
        else:
            response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    # Routers
    app.include_router(session.router)
    app.include_router(events.router)
    app.include_router(budget.router)
    app.include_router(timeline.router)
    app.include_router(vendors.router)
    app.include_router(ideas.router)
    app.include_router(compare.router)

    @app.get("/api/health")
    def health_check() -> dict:
        return {"status": "ok", "app": settings.app_name, "version": settings.version}

    # Static UI and template mounting for all-in-one container deployment
    base_dir = os.path.dirname(os.path.dirname(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=FileResponse, include_in_schema=False)
    def serve_frontend_root():
        candidates = [
            os.path.join(frontend_dir, "index.html"),
            os.path.join(templates_dir, "index.html"),
            os.path.join(base_dir, "index.html"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return FileResponse(c, media_type="text/html")
        return JSONResponse(status_code=404, content={"detail": "Frontend UI index not found."})

    if os.path.isdir(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    return app


app = create_app()
