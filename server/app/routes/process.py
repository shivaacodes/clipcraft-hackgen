"""
Video processing API routes for chunking, transcription, and vibe analysis.
"""

import os
import uuid
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Literal, Annotated
import logging
import requests
from urllib.parse import urlparse

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from ..services.whisper_service import WhisperCppService, TranscriptionManager
from ..services.llm_service import SimpleVibeAnalyzer, GeminiVibeAnalyzer, VibeAnalysisManager, list_gemini_models
from ..services.clip_generator import ClipGenerator, ClipGenerationManager
from ..services.video_renderer import VideoRenderer, VideoRenderingManager
from ..utils.chunking import ChunkingStrategy
from ..utils.performance_profiler import get_profiler, cleanup_profiler

logger = logging.getLogger(__name__)
router = APIRouter(tags=["video-processing"])

# Global service instances (in production, use dependency injection)
whisper_service = None
vibe_analyzer = None
transcription_manager = None
vibe_manager = None
clip_generator = None
clip_manager = None
video_renderer = None
render_manager = None

def get_services():
    """Initialize services if not already created."""
    global whisper_service, vibe_analyzer, transcription_manager, vibe_manager, clip_generator, clip_manager, video_renderer, render_manager
    
    if whisper_service is None:
        whisper_service = WhisperCppService(
            whisper_executable=os.getenv("WHISPER_EXECUTABLE", "whisper"),
            model_path=os.getenv("WHISPER_MODEL_PATH"),
            language=os.getenv("WHISPER_LANGUAGE", "auto"),
            threads=int(os.getenv("WHISPER_THREADS", "4"))
        )
        
    # LLM provider selection
    llm_provider = os.getenv("VIBE_LLM_PROVIDER", "claude").lower()
    if vibe_analyzer is None:
        if llm_provider == "gemini":
            vibe_analyzer = GeminiVibeAnalyzer(
                api_key=os.getenv("GEMINI_API_KEY"),
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
            )
        else:
            vibe_analyzer = SimpleVibeAnalyzer(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            )
    
    if transcription_manager is None:
        transcription_manager = TranscriptionManager(whisper_service)
        
    if vibe_manager is None:
        vibe_manager = VibeAnalysisManager(vibe_analyzer)
    
    if clip_generator is None:
        # Create clips directory
        clips_dir = os.path.join(os.getcwd(), "generated_clips")
        os.makedirs(clips_dir, exist_ok=True)
        clip_generator = ClipGenerator(output_base_dir=clips_dir)
    
    if clip_manager is None:
        clip_manager = ClipGenerationManager(clip_generator)
    
    if video_renderer is None:
        # Create rendered videos directory
        rendered_dir = os.path.join(os.getcwd(), "rendered_videos")
        os.makedirs(rendered_dir, exist_ok=True)
        video_renderer = VideoRenderer(output_base_dir=rendered_dir)
    
    if render_manager is None:
        render_manager = VideoRenderingManager(video_renderer)
    
    return transcription_manager, vibe_manager, clip_manager, render_manager

# Pydantic models for request/response
class ProjectContext(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    target_audience: Optional[str] = None
    selected_vibe: Optional[str] = None
    selected_age_group: Optional[str] = None

class ProcessingRequest(BaseModel):
    chunk_strategy: str = Field(default="adaptive", description="Chunking strategy: time, scene, or adaptive")
    include_vibe_analysis: bool = Field(default=True, description="Whether to perform vibe analysis")
    project_context: Optional[ProjectContext] = None

class CloudinaryProcessingRequest(BaseModel):
    video_url: str = Field(description="Cloudinary video URL")
    chunk_strategy: str = Field(default="adaptive", description="Chunking strategy: time, scene, or adaptive")
    include_vibe_analysis: bool = Field(default=True, description="Whether to perform vibe analysis")
    fast_mode: bool = Field(default=True, description="Whether to use fast mode for clip generation")
    project_context: Optional[ProjectContext] = None

class ProcessingStatus(BaseModel):
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: float
    current_step: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TimelineClip(BaseModel):
    type: Literal['clip'] = 'clip'
    timelineId: int
    id: int
    name: str
    duration: str
    clip_url: str
    thumbnail_url: Optional[str] = None
    startTime: str
    endTime: str
    confidence: float
    vibe: Optional[str] = None
    reason: Optional[str] = None
    scores: Optional[Dict] = None

class TimelineImage(BaseModel):
    type: Literal['image'] = 'image'
    timelineId: int
    id: int
    name: str
    duration: str
    url: str

class TimelineText(BaseModel):
    type: Literal['text'] = 'text'
    timelineId: int
    id: int
    name: str
    duration: str
    text: str

TimelineItem = Union[TimelineClip, TimelineImage, TimelineText]

class RenderRequest(BaseModel):
    timeline_clips: list[Annotated[TimelineItem, Field(discriminator='type')]]
    project_name: str = "final_video"
    bgm_filename: Optional[str] = None  # BGM filename if uploaded
    sfx_list: Optional[List[Dict[str, Any]]] = None  # SFX list: [{"path": str, "delay_ms": int}]
    bgm_regions: Optional[List[Dict[str, float]]] = None  # List of {start, duration} for selective BGM

class RenderStatus(BaseModel):
    job_id: str
    status: str  # "rendering", "completed", "failed"
    progress: float
    current_step: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory job storage (use Redis or database in production)
processing_jobs: Dict[str, ProcessingStatus] = {}
render_jobs: Dict[str, RenderStatus] = {}

def coerce_timeline_clip(item: dict, idx: int = 0) -> dict:
    item_type = item.get('type', 'clip')
    if item_type == 'clip':
        required = ['clip_url', 'duration', 'name', 'startTime', 'endTime']
        for field in required:
            if not item.get(field):
                raise ValueError(f"Timeline item {idx} (clip) missing required field: {field}")
        return {
            'type': 'clip',
            'timelineId': int(item.get('timelineId', idx)),
            'id': int(item.get('id', idx)),
            'name': str(item.get('name', f'Clip {idx+1}')),
            'duration': str(item.get('duration', '3')),
            'clip_url': str(item.get('clip_url', '')),
            'thumbnail_url': item.get('thumbnail_url', None),
            'startTime': str(item.get('startTime', '0:00')),
            'endTime': str(item.get('endTime', '0:03')),
            'confidence': float(item.get('confidence', 1.0)),
            'vibe': item.get('vibe', None),
            'reason': item.get('reason', None),
            'scores': item.get('scores', None),
        }
    elif item_type == 'image':
        required = ['url', 'duration', 'name']
        for field in required:
            if not item.get(field):
                raise ValueError(f"Timeline item {idx} (image) missing required field: {field}")
        return {
            'type': 'image',
            'timelineId': int(item.get('timelineId', idx)),
            'id': int(item.get('id', idx)),
            'name': str(item.get('name', f'Image {idx+1}')),
            'duration': str(item.get('duration', '3')),
            'url': item.get('url'),
        }
    elif item_type == 'text':
        required = ['text', 'duration', 'name']
        for field in required:
            if not item.get(field):
                raise ValueError(f"Timeline item {idx} (text) missing required field: {field}")
        return {
            'type': 'text',
            'timelineId': int(item.get('timelineId', idx)),
            'id': int(item.get('id', idx)),
            'name': str(item.get('name', f'Text {idx+1}')),
            'duration': str(item.get('duration', '3')),
            'text': item.get('text', ''),
        }
    else:
        # Unknown type, pass through as-is or raise error
        raise ValueError(f"Timeline item {idx} has unknown type: {item_type}")

@router.post("/upload-and-analyze")
async def upload_and_analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunk_strategy: str = "adaptive",
    include_vibe_analysis: bool = True,
    fast_mode: bool = True,
    project_context: Optional[str] = None  # JSON string
):
    """
    Upload video file and start processing pipeline.
    Returns job ID for tracking progress.
    """
    # Validate file
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        raise HTTPException(400, "Unsupported video format")
    
    if file.size and file.size > 500 * 1024 * 1024:  # 500MB limit
        raise HTTPException(400, "File too large (max 500MB)")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Parse project context
    context = None
    if project_context:
        try:
            import json
            context_data = json.loads(project_context)
            context = ProjectContext(**context_data)
        except Exception as e:
            logger.warning(f"Failed to parse project context: {e}")
    
    # Initialize job status
    processing_jobs[job_id] = ProcessingStatus(
        job_id=job_id,
        status="processing",
        progress=0.0,
        current_step="uploading"
    )
    
    # Read file content before starting background task
    file_content = await file.read()
    file_name = file.filename
    
    # Start background processing
    background_tasks.add_task(
        process_video_pipeline,
        job_id,
        file_content,
        file_name,
        chunk_strategy,
        include_vibe_analysis,
        fast_mode,
        context
    )
    
    return {"job_id": job_id, "status": "processing"}

@router.post("/process-cloudinary-video")
async def process_cloudinary_video(
    request: CloudinaryProcessingRequest,
    background_tasks: BackgroundTasks
):
    """
    Process video from Cloudinary URL.
    Returns job ID for tracking progress.
    """
    # Validate video URL
    try:
        parsed_url = urlparse(request.video_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(400, "Invalid video URL")
        
        # Check if it's a valid Cloudinary URL (optional validation)
        if "cloudinary.com" not in parsed_url.netloc:
            logger.warning(f"Non-Cloudinary URL provided: {request.video_url}")
    except Exception as e:
        raise HTTPException(400, f"Invalid video URL: {str(e)}")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    processing_jobs[job_id] = ProcessingStatus(
        job_id=job_id,
        status="processing",
        progress=0.0,
        current_step="downloading"
    )
    
    # Start background processing
    background_tasks.add_task(
        process_cloudinary_video_pipeline,
        job_id,
        request.video_url,
        request.chunk_strategy,
        request.include_vibe_analysis,
        request.fast_mode,
        request.project_context
    )
    
    return {"job_id": job_id, "status": "processing"}

@router.get("/status/{job_id}")
async def get_processing_status(job_id: str):
    """Get processing status for a job."""
    if job_id not in processing_jobs:
        raise HTTPException(404, "Job not found")
    
    return processing_jobs[job_id]

@router.get("/result/{job_id}")
async def get_processing_result(job_id: str):
    """Get final processing result."""
    if job_id not in processing_jobs:
        raise HTTPException(404, "Job not found")
    
    job = processing_jobs[job_id]
    if job.status != "completed":
        raise HTTPException(400, f"Job not completed (status: {job.status})")
    
    return job.result

@router.post("/analyze-text")
async def analyze_text_vibe(
    text: str,
    project_context: Optional[ProjectContext] = None
):
    """
    Direct text analysis endpoint for testing vibe analysis.
    """
    try:
        _, vibe_manager, _, _ = get_services()
        
        # Create mock transcription data
        mock_transcription = {
            "merged_transcription": {
                "text": text,
                "confidence": 0.9,
                "segments": []
            },
            "processing_stats": {
                "total_words": len(text.split()),
                "total_duration": 60.0,  # Mock duration
                "success_rate": 1.0
            },
            "chunks": []
        }
        
        # Analyze vibe
        result = await vibe_manager.analyze_video_vibe(
            mock_transcription,
            project_context.dict() if project_context else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in text vibe analysis: {e}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint to verify services are working."""
    try:
        transcription_manager, vibe_manager, clip_manager, render_manager = get_services()
        
        # Check whisper.cpp
        whisper_info = transcription_manager.whisper_service.get_model_info()
        
        # Check Claude API (without making expensive call)
        claude_info = {
            "model": vibe_manager.vibe_analyzer.model,
            "api_key_configured": bool(vibe_manager.vibe_analyzer.api_key)
        }
        
        return {
            "status": "healthy",
            "services": {
                "whisper": whisper_info,
                "claude": claude_info
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

async def process_video_pipeline(
    job_id: str,
    file_content: bytes,
    file_name: str,
    chunk_strategy: str,
    include_vibe_analysis: bool,
    fast_mode: bool,
    project_context: Optional[ProjectContext]
):
    """
    Background task for complete video processing pipeline.
    """
    try:
        # Get services
        transcription_manager, vibe_manager, clip_manager, render_manager = get_services()

        # Set language for this request if provided
        global whisper_service
        if project_context and getattr(project_context, "language", None):
            whisper_service.language = project_context.language
        else:
            whisper_service.language = os.getenv("WHISPER_LANGUAGE", "auto")
        
        # Update status
        processing_jobs[job_id].current_step = "saving_file"
        processing_jobs[job_id].progress = 10.0
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file_name}") as tmp_file:
            tmp_file.write(file_content)
            temp_video_path = tmp_file.name
        
        try:
            # Step 1: Transcription
            processing_jobs[job_id].current_step = "transcribing"
            processing_jobs[job_id].progress = 20.0
            
            async def transcription_progress(current, total, result):
                progress = 20.0 + (current / total) * 60.0  # 20-80% for transcription
                processing_jobs[job_id].progress = progress
                processing_jobs[job_id].current_step = f"transcribing_chunk_{current}_{total}"
            
            transcription_result = await transcription_manager.transcribe_video_file(
                temp_video_path,
                chunk_strategy=chunk_strategy,
                progress_callback=transcription_progress
            )
            
            # Step 2: Vibe Analysis (if requested)
            final_result = {"transcription": transcription_result}
            
            if include_vibe_analysis:
                processing_jobs[job_id].current_step = "analyzing_vibe"
                processing_jobs[job_id].progress = 85.0
                
                vibe_result = await vibe_manager.analyze_video_vibe(
                    transcription_result,
                    project_context.dict() if project_context else None
                )
                
                final_result["vibe_analysis"] = vibe_result
                
                # Step 3: Generate actual video clips
                processing_jobs[job_id].current_step = "generating_clips"
                processing_jobs[job_id].progress = 95.0
                
                final_result = await clip_manager.generate_clips_from_pipeline_result(
                    final_result,
                    temp_video_path,
                    max_clips=3,  # Increased to 3 for shorter clips
                    fast_mode=fast_mode
                )
            
            # Complete
            processing_jobs[job_id].status = "completed"
            processing_jobs[job_id].progress = 100.0
            processing_jobs[job_id].current_step = "completed"
            processing_jobs[job_id].result = final_result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_video_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
    
    except Exception as e:
        logger.error(f"Processing pipeline failed for job {job_id}: {e}")
        processing_jobs[job_id].status = "failed"
        processing_jobs[job_id].error = str(e)
        processing_jobs[job_id].current_step = "failed"

async def process_cloudinary_video_pipeline(
    job_id: str,
    video_url: str,
    chunk_strategy: str,
    include_vibe_analysis: bool,
    fast_mode: bool,
    project_context: Optional[ProjectContext]
):
    """
    Background task for processing Cloudinary video URLs with performance profiling.
    """
    profiler = get_profiler(job_id)
    
    try:
        # Get services
        transcription_manager, vibe_manager, clip_manager, render_manager = get_services()

        # Set language for this request if provided
        global whisper_service
        if project_context and getattr(project_context, "language", None):
            whisper_service.language = project_context.language
        else:
            whisper_service.language = os.getenv("WHISPER_LANGUAGE", "auto")
        
        # Update status
        processing_jobs[job_id].current_step = "downloading"
        processing_jobs[job_id].progress = 5.0
        
        # Download video from Cloudinary
        temp_video_path = None
        try:
            with profiler.profile("video_download", {"url": video_url, "fast_mode": fast_mode}):
                # Download the video file
                response = requests.get(video_url, stream=True, timeout=60)
                response.raise_for_status()
                
                # Save to temporary file
                suffix = ".mp4"  # Default suffix, could be inferred from URL
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    # Update progress during download
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
                            downloaded_size += len(chunk)
                            if total_size > 0:
                                download_progress = 5.0 + (downloaded_size / total_size) * 15.0
                                processing_jobs[job_id].progress = min(download_progress, 20.0)
                    
                    temp_video_path = tmp_file.name
            
            processing_jobs[job_id].current_step = "download_complete"
            processing_jobs[job_id].progress = 20.0
            
            # Step 1: Transcription with profiling
            processing_jobs[job_id].current_step = "transcribing"
            processing_jobs[job_id].progress = 25.0
            
            async def transcription_progress(current, total, result):
                progress = 25.0 + (current / total) * 60.0  # 25-85% for transcription
                processing_jobs[job_id].progress = progress
                processing_jobs[job_id].current_step = f"transcribing_chunk_{current}_{total}"
            
            with profiler.profile("transcription", {"strategy": chunk_strategy, "fast_mode": fast_mode}):
                transcription_result = await transcription_manager.transcribe_video_file(
                    temp_video_path,
                    chunk_strategy=chunk_strategy,
                    progress_callback=transcription_progress
                )
            
            # Step 2: Vibe Analysis (if requested)
            final_result = {"transcription": transcription_result}
            
            if include_vibe_analysis:
                processing_jobs[job_id].current_step = "analyzing_vibe"
                processing_jobs[job_id].progress = 85.0
                
                with profiler.profile("vibe_analysis", {"vibe": project_context.selected_vibe if project_context else None}):
                    vibe_result = await vibe_manager.analyze_video_vibe(
                        transcription_result,
                        project_context.dict() if project_context else None
                    )
                
                final_result["vibe_analysis"] = vibe_result
                
                # Step 3: Generate actual video clips
                processing_jobs[job_id].current_step = "generating_clips"
                processing_jobs[job_id].progress = 95.0
                
                with profiler.profile("clip_generation", {"fast_mode": fast_mode, "max_clips": 5}):
                    final_result = await clip_manager.generate_clips_from_pipeline_result(
                        final_result,
                        temp_video_path,
                        max_clips=5,  # Increased to 5 for shorter clips
                        fast_mode=fast_mode
                    )
            
            # Complete and show performance summary
            processing_jobs[job_id].status = "completed"
            processing_jobs[job_id].progress = 100.0
            processing_jobs[job_id].current_step = "completed"
            processing_jobs[job_id].result = final_result
            
            # Add performance data to result
            performance_summary = profiler.get_summary()
            bottleneck_analysis = profiler.get_bottleneck_analysis()
            
            processing_jobs[job_id].result["performance"] = {
                "summary": performance_summary,
                "bottlenecks": bottleneck_analysis,
                "total_time": performance_summary["total_duration"],
                "slowest_operations": profiler.get_slowest_operations(3)
            }
            
            # Print performance summary to logs
            profiler.print_summary()
            
            # Log bottleneck analysis
            if bottleneck_analysis["bottlenecks"]:
                logger.warning(f"🐌 Performance bottlenecks found for job {job_id}:")
                for bottleneck in bottleneck_analysis["bottlenecks"]:
                    logger.warning(f"   - {bottleneck['operation']}: {bottleneck['duration']:.2f}s ({bottleneck['percentage']:.1f}%)")
            
            logger.info(f"✅ Job {job_id} completed in {performance_summary['total_duration']:.2f}s")
            
        except requests.RequestException as e:
            logger.error(f"Failed to download video from {video_url}: {e}")
            processing_jobs[job_id].status = "failed"
            processing_jobs[job_id].error = f"Download failed: {str(e)}"
            processing_jobs[job_id].current_step = "download_failed"
            return
            
        finally:
            # Clean up temporary file
            if temp_video_path:
                try:
                    os.unlink(temp_video_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
    
    except Exception as e:
        logger.error(f"Cloudinary processing pipeline failed for job {job_id}: {e}")
        processing_jobs[job_id].status = "failed"
        processing_jobs[job_id].error = str(e)
        processing_jobs[job_id].current_step = "failed"
        
        # Still save performance data even on failure
        if profiler.results:
            performance_summary = profiler.get_summary()
            processing_jobs[job_id].result = processing_jobs[job_id].result or {}
            processing_jobs[job_id].result["performance"] = {
                "summary": performance_summary,
                "total_time": performance_summary["total_duration"],
                "error": "Pipeline failed partway through"
            }
    
    finally:
        # Clean up profiler
        cleanup_profiler(job_id)

@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job data to free memory."""
    if job_id in processing_jobs:
        del processing_jobs[job_id]
        return {"message": "Job deleted"}
    else:
        raise HTTPException(404, "Job not found")

@router.get("/jobs")
async def list_jobs():
    """List all current jobs (for debugging)."""
    return {
        "total_jobs": len(processing_jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "current_step": job.current_step
            }
            for job in processing_jobs.values()
        ]
    }

# Configuration endpoints
@router.get("/config/whisper")
async def get_whisper_config():
    """Get current whisper configuration."""
    transcription_manager, _, _, _ = get_services()
    return transcription_manager.whisper_service.get_model_info()

@router.get("/config/vibe-categories")
async def get_vibe_categories():
    """Get available vibe categories for analysis."""
    _, vibe_manager, _, _ = get_services()
    return {
        "vibes": vibe_manager.vibe_analyzer.VIBES,
        "age_groups": vibe_manager.vibe_analyzer.AGE_GROUPS
    }

@router.get("/clips/{filename}")
async def get_clip_file(filename: str):
    """Serve generated clip files."""
    clips_dir = os.path.join(os.getcwd(), "generated_clips")
    file_path = os.path.join(clips_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip file not found")
    
    # Determine media type based on file extension
    if filename.endswith('.mp4'):
        media_type = "video/mp4"
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        media_type = "image/jpeg"
    elif filename.endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename
    )

@router.get("/test-clips")
async def get_test_clips():
    """Return test clips data for frontend testing."""
    clips_dir = os.path.join(os.getcwd(), "generated_clips")
    
    # Find actual generated clips
    clips = []
    thumbnails = []
    
    if os.path.exists(clips_dir):
        for file in os.listdir(clips_dir):
            if file.startswith("clip_") and file.endswith(".mp4"):
                clips.append(file)
            elif file.startswith("thumb_") and file.endswith(".jpg"):
                thumbnails.append(file)
    
    # Create test response
    test_clips = []
    for i, clip_file in enumerate(clips[:3]):  # Limit to 3 clips
        # Extract info from filename
        parts = clip_file.replace(".mp4", "").split("_")
        if len(parts) >= 4:
            clip_num = parts[1]
            clip_id = parts[2]
            time_range = parts[3]
            
            # Find matching thumbnail
            thumb_file = f"thumb_{clip_num}_{clip_id}_{time_range.split('-')[0]}.jpg"
            
            clip_data = {
                "title": f"Happy Clip {i+1}",
                "start_time": 5.0 + (i * 8),
                "end_time": 11.0 + (i * 8),
                "duration": 6.0,
                "vibe": "Happy",
                "rank": i + 1,
                "scores": {
                    "overall": 85 - (i * 5),
                    "vibe_match": 90 - (i * 5),
                    "age_group_match": 80 - (i * 5),
                    "clip_potential": 85 - (i * 5)
                },
                "reason": f"This segment has positive energy and engaging content suitable for happy vibes.",
                "clip_url": f"/api/v1/process/clips/{clip_file}",
                "thumbnail_url": f"/api/v1/process/clips/{thumb_file}" if thumb_file in thumbnails else None
            }
            
            test_clips.append(clip_data)
    
    return {
        "vibe_analysis": {
            "vibe_analysis": {
                "selected_vibe": "Happy",
                "selected_age_group": "young-adults",
                "clips_found": len(test_clips),
                "top_clips": test_clips
            }
        },
        "status": "success"
    }

@router.post("/render-timeline")
async def render_timeline_video(
    request: Any = Body(...),
    background_tasks: BackgroundTasks = None
):
    """
    Render timeline clips into a final video. Supports BGM and SFX.
    Returns job ID for tracking progress.
    """
    try:
        validated_request = RenderRequest(**request)
    except Exception as e:
        logger.error(f"RenderRequest validation failed: {e}")
        raise HTTPException(422, f"RenderRequest validation failed: {e}")
    timeline_items = validated_request.timeline_clips
    project_name = validated_request.project_name
    bgm_filename = validated_request.bgm_filename
    sfx_list = validated_request.sfx_list or []
    bgm_regions = validated_request.bgm_regions or []
    job_id = str(uuid.uuid4())
    render_jobs[job_id] = RenderStatus(
        job_id=job_id,
        status="rendering",
        progress=0.0,
        current_step="preparing"
    )
    background_tasks.add_task(
        render_timeline_background,
        job_id,
        timeline_items,
        project_name,
        bgm_filename,
        sfx_list,
        bgm_regions
    )
    return {"job_id": job_id, "status": "rendering"}

@router.get("/render-status/{job_id}")
async def get_render_status(job_id: str):
    """Get rendering status for a job."""
    if job_id not in render_jobs:
        raise HTTPException(404, "Render job not found")
    
    return render_jobs[job_id]

@router.get("/render-result/{job_id}")
async def get_render_result(job_id: str):
    """Get final rendering result."""
    if job_id not in render_jobs:
        raise HTTPException(404, "Render job not found")
    
    job = render_jobs[job_id]
    if job.status != "completed":
        raise HTTPException(400, f"Render job not completed (status: {job.status})")
    
    return job.result

@router.get("/rendered-videos/{filename}")
async def get_rendered_video_file(filename: str):
    """Serve rendered video files."""
    rendered_dir = os.path.join(os.getcwd(), "rendered_videos")
    file_path = os.path.join(rendered_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Rendered video file not found")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )

@router.get("/rendered-videos")
async def list_rendered_videos():
    """List all rendered videos."""
    try:
        _, _, _, render_manager = get_services()
        videos = render_manager.video_renderer.get_rendered_videos()
        return {"videos": videos, "total": len(videos)}
    except Exception as e:
        logger.error(f"Error listing rendered videos: {e}")
        raise HTTPException(500, f"Failed to list videos: {str(e)}")

@router.get("/performance/{job_id}")
async def get_performance_analysis(job_id: str):
    """Get detailed performance analysis for a job."""
    if job_id not in processing_jobs:
        raise HTTPException(404, "Job not found")
    
    job = processing_jobs[job_id]
    
    if not job.result or "performance" not in job.result:
        raise HTTPException(400, "No performance data available for this job")
    
    return job.result["performance"]

@router.get("/performance")
async def get_recent_performance():
    """Get performance data for recent jobs."""
    recent_jobs = []
    
    for job_id, job in processing_jobs.items():
        if job.result and "performance" in job.result:
            perf = job.result["performance"]
            recent_jobs.append({
                "job_id": job_id,
                "status": job.status,
                "total_time": perf.get("total_time", 0),
                "bottlenecks": len(perf.get("bottlenecks", {}).get("bottlenecks", [])),
                "slowest_operation": perf.get("slowest_operations", [{}])[0].get("name", "Unknown") if perf.get("slowest_operations") else "Unknown"
            })
    
    # Sort by total time (slowest first)
    recent_jobs.sort(key=lambda x: x["total_time"], reverse=True)
    
    return {
        "recent_jobs": recent_jobs[:10],  # Last 10 jobs
        "total_jobs": len(recent_jobs)
    }

@router.delete("/render-job/{job_id}")
async def delete_render_job(job_id: str):
    """Delete render job data to free memory."""
    if job_id in render_jobs:
        del render_jobs[job_id]
        return {"message": "Render job deleted"}
    else:
        raise HTTPException(404, "Render job not found")

async def render_timeline_background(
    job_id: str,
    timeline_clips: List[TimelineItem],
    project_name: str,
    bgm_filename: Optional[str],
    sfx_list: Optional[List[Dict[str, Any]]] = None,
    bgm_regions: Optional[List[Dict[str, float]]] = None
):
    """Background task for rendering timeline video. Supports BGM and SFX."""
    try:
        _, _, _, render_manager = get_services()
        render_jobs[job_id].current_step = "initializing"
        render_jobs[job_id].progress = 10.0
        timeline_data = {
            'timeline_clips': [clip.dict() for clip in timeline_clips]
        }
        if bgm_filename:
            bgm_dir = os.path.join(os.getcwd(), "uploaded_bgm")
            bgm_path = os.path.join(bgm_dir, bgm_filename)
            if os.path.exists(bgm_path):
                timeline_data['bgm_path'] = bgm_path
                render_jobs[job_id].current_step = "preparing_with_bgm"
            else:
                logger.warning(f"BGM file not found: {bgm_path}")
        if sfx_list:
            timeline_data['sfx_list'] = sfx_list
        if bgm_regions:
            timeline_data['bgm_regions'] = bgm_regions
        render_jobs[job_id].progress = 25.0
        render_jobs[job_id].current_step = "stitching_clips"
        render_jobs[job_id].progress = 50.0
        render_result = await render_manager.render_project_video(
            timeline_data, project_name
        )
        render_jobs[job_id].status = "completed"
        render_jobs[job_id].progress = 100.0
        render_jobs[job_id].current_step = "completed"
        render_jobs[job_id].result = render_result
        logger.info(f"✅ Timeline rendering completed for job {job_id}")
    except Exception as e:
        logger.error(f"Timeline rendering failed for job {job_id}: {e}")
        render_jobs[job_id].status = "failed"
        render_jobs[job_id].error = str(e)
        render_jobs[job_id].current_step = "failed"

@router.get("/gemini-models")
async def get_gemini_models():
    """Return the list of available Gemini models for the configured API key."""
    try:
        import google.generativeai as genai
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        models = genai.list_models()
        model_names = [m.name for m in models]
        return {"models": model_names}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})