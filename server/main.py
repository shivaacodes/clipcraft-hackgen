# server/main.py

"""
ClipCraft FastAPI server — Transcribe 🎙️, Analyze 🧠, Export 🎬.
"""

import os
import logging
import subprocess
from contextlib import asynccontextmanager
import shutil

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

# --- Define clip output directory at the top level in main.py ---
# os.path.dirname(__file__) is 'server/'
CLIPS_STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "public", "extracted_clips"))
print(CLIPS_STORAGE_PATH)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting ClipCraft backend server...")

    required_vars = ["ANTHROPIC_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.warning(f"⚠️ Missing environment variables: {missing}. Some features might be unavailable.")

    try:
        whisper_exec = os.getenv("WHISPER_EXECUTABLE", "whisper")
        subprocess.run([whisper_exec, "--help"], capture_output=True, timeout=5)
    except Exception as e:
        logger.warning(f"⚠️ Whisper executable not found or not working: {e}")

    # Ensure temporary upload directory exists for find_by_image functionality
    temp_upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_uploads")) # Define temp_uploads relative to server/
    os.makedirs(temp_upload_dir, exist_ok=True)
    logger.info(f"Ensured temporary upload directory '{temp_upload_dir}' exists.")

    # Ensure output directory for extracted clips exists
    os.makedirs(CLIPS_STORAGE_PATH, exist_ok=True)
    logger.info(f"Ensured clip output directory '{CLIPS_STORAGE_PATH}' exists.")

    yield
    logger.info("🛑 Shutting down ClipCraft backend server")
    # Optional: Cleanup temp_uploads directory on shutdown if desired
    if os.path.exists(temp_upload_dir) and os.path.isdir(temp_upload_dir):
        logger.info(f"Cleaning up temporary upload directory '{temp_upload_dir}' on shutdown...")
        try:
            shutil.rmtree(temp_upload_dir)
            logger.info(f"Successfully removed '{temp_upload_dir}'.")
        except Exception as e:
            logger.error(f"Error cleaning up '{temp_upload_dir}': {e}")


app = FastAPI(
    title="ClipCraft API",
    description="Personalized video clip generator using Whisper & Claude",
    version="0.1.0",
    lifespan=lifespan,
)

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

from app.routes.find import router as find_router
app.include_router(find_router, prefix="/api/v1/find", tags=["Find"])

# --- Include the find_by_image router ---
from app.routes.find_by_image import router as find_by_image_router
app.include_router(find_by_image_router, prefix="/api/v1/find", tags=["Find"]) # The endpoint will be /api/v1/find/by-image

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
            "find_by_image_clips": "/api/v1/find/by-image",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClipCraft API"}

# This section assumes 'titan/public/assets/images' path.
# If 'titan' is a sibling of 'server', then you might need to adjust.
# Assuming 'titan' is at the ROOT level, and this `main.py` is inside 'server'.
# So from 'server/main.py', '../' would be 'ROOT/'
PROJECT_ROOT_FOR_TITAN = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # This goes to ROOT/
UPLOAD_DIR = os.path.join(PROJECT_ROOT_FOR_TITAN, "titan/public/assets/images") # Corrected path for titan assets

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    public_url = f"/assets/images/{file.filename}"
    return JSONResponse({"url": public_url})

# Ensure the images directory exists before mounting
os.makedirs(os.path.join(PROJECT_ROOT_FOR_TITAN, "titan/public/assets/images"), exist_ok=True)
# Serve static files from /assets/images - this will resolve to ROOT/titan/public/assets/images
app.mount("/assets/images", StaticFiles(directory=os.path.join(PROJECT_ROOT_FOR_TITAN, "titan/public/assets/images")), name="assets-images")

# --- Mount the directory for extracted video clips ---
# This path '/extracted_clips' will be the URL prefix for accessing clips
# It will serve from CLIPS_STORAGE_PATH, which is ROOT/server/public/extracted_clips
app.mount("/extracted_clips", StaticFiles(directory=CLIPS_STORAGE_PATH), name="extracted_clips")
logger.info(f"Mounted static directory '/extracted_clips' from '{CLIPS_STORAGE_PATH}'")


if __name__ == "__main__":
    print(CLIPS_STORAGE_PATH)
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )