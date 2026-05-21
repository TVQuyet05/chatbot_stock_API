"""
Main FastAPI entrypoint.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import time

from src.core.config import get_settings
from src.db.postgres import init_db, close_db
from src.db.milvus_store import create_milvus_store
from src.rag.embedding import get_embedding_model
from src.api.router import router as api_router
from src.auth.router import router as auth_router, admin_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: Startup and Shutdown."""
    settings = get_settings()
    logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # 1. Initialize PostgreSql tables
    await init_db()

    # 2. Warm up embedding model (pre-load)
    logger.info("Initializing embedding model...")
    get_embedding_model()

    # 3. Check Milvus connection
    logger.info("Checking Milvus connection...")
    try:
        create_milvus_store(embeddings=get_embedding_model())
        logger.info("Milvus connection verified")
    except Exception as e:
        logger.error("Failed to connect to Milvus: %s", e)

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(
    title=get_settings().APP_NAME,
    version=get_settings().APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(api_router)

# Mount Developer Portal (static files)
# We need to create the directory first if we haven't
portal_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "portal")
if os.path.exists(portal_dir):
    app.mount("/portal", StaticFiles(directory=portal_dir), name="portal")

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to developer portal or show index."""
    index_path = os.path.join(portal_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Welcome to Stock Law Advisory API. Visit /docs for API documentation."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
