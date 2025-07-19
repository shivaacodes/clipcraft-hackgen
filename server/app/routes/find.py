"""
Find API route: Accepts a video file and a query (text or voice), runs chunking, transcription, searches for matching segments, and generates video clips for matches.
"""

import os
import tempfile
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from ..services.whisper_service import WhisperCppService
from ..services.clip_generator import ClipGenerator
from ..utils.chunking import ChunkingStrategy
import unicodedata
import re
from rapidfuzz import fuzz

router = APIRouter(tags=["find"])

# Initialize services (reuse from process.py if possible)
whisper_service = WhisperCppService()
clip_generator = ClipGenerator()

@router.post("/find")
async def find_clip(
    video: UploadFile = File(...),
    query: str = Form(...),
    chunk_strategy: str = Form("adaptive"),
    max_results: int = Form(3),
    fuzzy: bool = Form(True),
    language: str = Form("auto")  # Add language selection, default auto
):
    """
    Accept a video file and a query, return matching video clips.
    """
    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{video.filename}") as tmp_file:
        tmp_file.write(await video.read())
        temp_video_path = tmp_file.name

    try:
        # Step 1: Chunk video into audio segments
        chunks = ChunkingStrategy.chunk_video(temp_video_path, tempfile.gettempdir(), strategy=chunk_strategy)
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to chunk video.")

        # Step 2: Transcribe each chunk (pass language to use Sarvam for Malayalam)
        segments = []
        for chunk in chunks:
            result = await whisper_service.transcribe_audio(chunk["path"], language=language)
            print(f"[FIND DEBUG] Sarvam result for chunk {chunk['path']}: {result}")
            if result.get("segments"):
                for seg in result["segments"]:
                    segments.append({
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text"),
                        "chunk_path": chunk["path"]
                    })
            elif result.get("text"):
                # Sarvam returns the whole chunk as 'text'
                segments.append({
                    "start": None,
                    "end": None,
                    "text": result["text"],
                    "chunk_path": chunk["path"]
                })
        print(f"[FIND DEBUG] Query: {query}")
        for seg in segments:
            print(f"[FIND DEBUG] Segment: {seg['text']}")

        # Step 3: Search for matching segments (robust Unicode/fuzzy match)
        def normalize_text(text):
            # For Malayalam and other Indic scripts, only NFC normalize and lowercase
            return unicodedata.normalize('NFC', text).strip().lower()

        query_norm = normalize_text(query)
        matches = []
        for seg in segments:
            seg_norm = normalize_text(seg["text"])
            # Fuzzy match: allow >80% similarity or substring
            if query_norm in seg_norm or fuzz.partial_ratio(query_norm, seg_norm) > 80:
                chunk = next((c for c in chunks if c["path"] == seg["chunk_path"]), None)
                if chunk:
                    matches.append({
                        "chunk_start": chunk["start_time"],
                        "chunk_end": chunk["end_time"],
                        "segment_start": seg["start"],
                        "segment_end": seg["end"],
                        "text": seg["text"],
                        "chunk_path": seg["chunk_path"]
                    })
        top_matches = matches[:max_results]

        # Step 4: Generate video clips for matches
        results = []
        for idx, match in enumerate(top_matches):
            clip_data = {
                "start_time": match["chunk_start"],
                "end_time": match["chunk_end"],
                "title": f"Find Clip {idx+1}"
            }
            clip_info = await clip_generator._generate_single_clip(
                video_path=temp_video_path,
                clip_data=clip_data,
                clip_number=idx,
                fast_mode=False
            )
            if clip_info:
                results.append({
                    "video_url": clip_info["url"],
                    "thumbnail_url": clip_info.get("thumbnail_url"),
                    "start": match["chunk_start"],
                    "end": match["chunk_end"],
                    "transcript": match["text"]
                })

        return JSONResponse({"results": results, "segments": segments})
    finally:
        try:
            os.unlink(temp_video_path)
        except Exception:
            pass 