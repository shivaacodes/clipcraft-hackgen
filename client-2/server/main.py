"""
ClipCraft FastAPI server — Transcribe 🎙️, Analyze 🧠, Export 🎬.
"""

import os
import logging
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
)
logger = logging.getLogger("clipcraft")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for ClipCraft server."""
    logger.info("🚀 Starting ClipCraft backend server...")

    # Required env checks
    required_vars = ["ANTHROPIC_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"❌ Missing environment variables: {missing}")

    # Check whisper.cpp CLI availability
    try:
        whisper_exec = os.getenv("WHISPER_EXECUTABLE", "whisper")
        subprocess.run([whisper_exec, "--help"], capture_output=True, timeout=5)
    except Exception as e:
        logger.warning(f"⚠️ Whisper executable not found or not working: {e}")

    logger.info("✅ ClipCraft backend initialized")
    yield
    logger.info("🛑 Shutting down ClipCraft backend server")

# Create FastAPI app
app = FastAPI(
    title="ClipCraft API",
    description="Personalized video clip generator using Whisper & Claude",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",        # Next.js dev
        "https://clipcraft.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.routes.process import router as process_router
app.include_router(process_router, prefix="/api/v1/process", tags=["Process"])

# Register the find router
from app.routes.find import router as find_router
app.include_router(find_router, prefix="/api/v1/find", tags=["Find"])

# Root route
@app.get("/")
async def root():
    return {
        "name": "ClipCraft",
        "status": "running",
        "description": "ClipCraft backend for transcription, vibe analysis, and export",
        "routes": {
            "upload_and_analyze": "/api/v1/process/upload-and-analyze",
            "job_status": "/api/v1/process/status/{job_id}",
            "job_result": "/api/v1/process/result/{job_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClipCraft API"}

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "titan/public/assets/images")

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    # Local URL for dev (adjust if using ngrok later)
    public_url = f"/assets/images/{file.filename}"
    return JSONResponse({"url": public_url})

# Ensure the images directory exists before mounting
os.makedirs("titan/public/assets/images", exist_ok=True)
# Serve static files from /assets/images
app.mount("/assets/images", StaticFiles(directory="titan/public/assets/images"), name="assets-images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
