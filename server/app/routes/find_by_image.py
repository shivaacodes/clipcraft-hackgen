import cv2
import face_recognition
import numpy as np
import os
import sys
import threading
import queue
import time
import shutil
import logging
import subprocess # New: For FFmpeg

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Tuple, Dict, Any

# Get the logger instance from main.py or configure it similarly
logger = logging.getLogger("clipcraft")

router = APIRouter()

# --- Configuration for output clips ---
# Base directory for all project assets (assuming project root is 'ClipCraft' from main.py)
# Adjust this path based on your actual project structure.
# For example, if main.py is in 'ClipCraft/main.py' and clips should go into 'ClipCraft/public/clips'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')) # Adjust based on main.py's PROJECT_ROOT logic
CLIPS_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../public', 'extracted_clips'))
# Make sure this directory is configured as a static files mount point in main.py if not already.
# I'll add this to main.py later.

# --- FrameReader Class (unchanged, but added more robust queue handling) ---
class FrameReader:
    def __init__(self, video_path, queue_max_size=128):
        self.video_path = video_path
        self.cap = None
        self.q = queue.Queue(maxsize=queue_max_size)
        self.stopped = False
        self.thread = threading.Thread(target=self._reader_loop, args=())
        self.thread.daemon = True

    def start(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            logger.error(f"Error: Could not open video file '{self.video_path}' in FrameReader.")
            self.stopped = True
            return None
        self.thread.start()
        return self

    def _reader_loop(self):
        while not self.stopped:
            if not self.q.full():
                if self.cap is None or not self.cap.isOpened():
                    self.stopped = True
                    break
                ret, frame = self.cap.read()
                if not ret:
                    self.stopped = True
                    break
                try:
                    self.q.put(frame, block=True, timeout=5) # Add timeout for put
                except queue.Full:
                    logger.warning("FrameReader queue is full, skipping frame.")
                    time.sleep(0.01) # Small sleep if full
            else:
                time.sleep(0.001)

    def read(self):
        if self.q.empty() and self.stopped:
            return None
        try:
            return self.q.get(timeout=1)
        except queue.Empty:
            return None

    def running(self):
        return not self.stopped or not self.q.empty()

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join(timeout=5) # Join with a timeout
            if self.thread.is_alive():
                logger.warning("FrameReader thread did not terminate gracefully.")
        if self.cap:
            self.cap.release()
        logger.info("FrameReader stopped and resources released.")

# --- extract_character_clips Function (unchanged logic, only return timestamps) ---
def extract_character_clips(video_path: str, character_image_path: str, tolerance: float = 0.6, frames_after_detection: int = 30, scale_factor: float = 1) -> List[Tuple[float, float]]:
    """
    Searches a video for a specific character and extracts clips where the character is present.
    This version only generates timestamps.
    """

    if sys.version_info >= (3, 13):
        logger.warning(
            "You are using Python 3.13 or newer. face_recognition (and its underlying dlib library) "
            "might not have full, stable support for this version yet. If you encounter issues, "
            "consider trying Python 3.10, 3.11, or 3.12 in a virtual environment."
        )

    try:
        character_image = face_recognition.load_image_file(character_image_path)
        character_face_encodings = face_recognition.face_encodings(character_image)

        if not character_face_encodings:
            logger.error(
                f"No face found in the character image '{character_image_path}'. "
                "Please provide a clear image of the character's face."
            )
            return []

        known_character_encoding = character_face_encodings[0]
        logger.info(f"Character '{os.path.basename(character_image_path)}' encoding loaded successfully.")

    except FileNotFoundError:
        logger.error(f"Character image not found at '{character_image_path}'.")
        return []
    except Exception as e:
        logger.error(f"Error loading or encoding character image: {e}")
        return []

    frame_reader = FrameReader(video_path)
    if not frame_reader.start():
        return []

    fps = int(frame_reader.cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        logger.warning(f"FPS is 0 for video '{video_path}'. Cannot process timestamps accurately.")
        frame_reader.stop()
        return []

    width = int(frame_reader.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(frame_reader.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    recording_active = False
    frames_since_last_detection = 0

    clip_timestamps = []
    current_clip_start_frame = -1

    logger.info("Starting multi-threaded video processing for timestamp extraction...")
    logger.info(f"Video resolution: {width}x{height}, FPS: {fps}")
    logger.info(f"Processing frames at scale factor: {scale_factor}")

    frame_count = 0
    while frame_reader.running():
        frame = frame_reader.read()
        if frame is None:
            break

        frame_count += 1
        current_time_seconds = frame_count / fps

        if scale_factor != 1.0:
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        else:
            small_frame = frame

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)

        face_encodings = []
        if face_locations:
            try:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            except Exception as e:
                logger.error(f"Error getting face encodings for frame {frame_count}: {e}")
                logger.debug(f"Debug Info: frame shape={rgb_small_frame.shape}, face_locations={face_locations}")
                face_encodings = []

        character_found_in_frame = False
        for i, face_encoding in enumerate(face_encodings):
            matches = face_recognition.compare_faces([known_character_encoding], face_encoding, tolerance=tolerance)
            
            if True in matches:
                character_found_in_frame = True
                frames_since_last_detection = 0
                break

        if character_found_in_frame:
            if not recording_active:
                recording_active = True
                current_clip_start_frame = frame_count
                logger.info(f"Character detected. Starting new timestamp period at time {current_time_seconds:.2f}s")
        else:
            if recording_active:
                frames_since_last_detection += 1
                if frames_since_last_detection > frames_after_detection:
                    recording_active = False
                    
                    clip_end_frame = frame_count - 1
                    clip_end_time = clip_end_frame / fps
                    if current_clip_start_frame != -1:
                        clip_start_time = current_clip_start_frame / fps
                        clip_timestamps.append((clip_start_time, clip_end_time))
                    
                    frames_since_last_detection = 0
                    logger.info(f"Character not detected for {frames_after_detection} frames. Ending current timestamp period. Duration: {clip_end_time - clip_start_time:.2f}s")
                    current_clip_start_frame = -1
            
    if recording_active and current_clip_start_frame != -1:
        clip_end_frame = frame_count
        clip_end_time = clip_end_frame / fps
        clip_start_time = current_clip_start_frame / fps
        clip_timestamps.append((clip_start_time, clip_end_time))

    frame_reader.stop()
    cv2.destroyAllWindows()
    logger.info("Video processing for timestamps complete.")
    
    logger.info(f"Found {len(clip_timestamps)} periods where the character was present.")
    
    return clip_timestamps

# --- NEW: Function to cut video clips using FFmpeg ---
def cut_video_clip(input_video_path: str, start_time: float, end_time: float, output_path: str) -> None:
    """
    Cuts a video clip using FFmpeg from start_time to end_time.

    Args:
        input_video_path (str): Path to the original video file.
        start_time (float): Start time of the clip in seconds.
        end_time (float): End time of the clip in seconds.
        output_path (str): Path where the output clip will be saved.
    """
    duration = end_time - start_time
    if duration <= 0:
        logger.warning(f"Clip duration is non-positive ({duration:.2f}s) for {input_video_path} from {start_time:.2f}s to {end_time:.2f}s. Skipping.")
        return

    # FFmpeg command:
    # -y: Overwrite output file without asking
    # -i: Input file
    # -ss: Start time (seek to this time before decoding)
    # -t: Duration
    # -c:v copy -c:a copy: Copy video and audio streams without re-encoding
    #     This is much faster but might not work perfectly with all codecs/formats
    #     For robustness, if quality is not critical, or for specific formats,
    #     you might use re-encoding options like -c:v libx264 -preset veryfast -crf 23 -c:a aac
    #     For this example, we'll stick to copy for speed.
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    command = [
        "ffmpeg",
        "-y",                   # Overwrite output files without asking
        "-i", input_video_path,
        "-ss", str(start_time),
        "-to", str(end_time),   # Using -to for end time
        "-c", "copy",           # Copy video and audio streams without re-encoding for speed
        output_path
    ]
    
    logger.info(f"Executing FFmpeg command: {' '.join(command)}")
    try:
        # Use subprocess.run for simpler execution and error handling
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"FFmpeg stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"FFmpeg stderr: {result.stderr}") # FFmpeg often outputs progress to stderr
        logger.info(f"Clip saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed to cut clip from {start_time:.2f}s to {end_time:.2f}s for {input_video_path}. Error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to process video clip with FFmpeg: {e.stderr}")
    except FileNotFoundError:
        logger.error("FFmpeg executable not found. Please ensure FFmpeg is installed and in your system's PATH.")
        raise HTTPException(status_code=500, detail="FFmpeg not found on the server.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while cutting video clip: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# --- FastAPI Endpoint ---
@router.post("/by-image")
async def find_clips_by_image(video_file: UploadFile = File(...), image_file: UploadFile = File(...)) -> JSONResponse:
    """
    API endpoint to receive a video and an image, process them,
    find character occurrences, cut clips, and return clip URLs.
    """
    if not video_file.filename or not image_file.filename:
        raise HTTPException(status_code=400, detail="Video and image files are required.")

    video_ext = os.path.splitext(video_file.filename)[1].lower()
    image_ext = os.path.splitext(image_file.filename)[1].lower()

    if video_ext not in ('.mp4', '.avi', '.mov', '.mkv', '.webm'):
        raise HTTPException(status_code=400, detail=f"Invalid video file format '{video_ext}'. Supported: MP4, AVI, MOV, MKV, WebM.")
    if image_ext not in ('.png', '.jpg', '.jpeg'):
        raise HTTPException(status_code=400, detail=f"Invalid image file format '{image_ext}'. Supported: PNG, JPG, JPEG.")

    # Define a temporary directory for uploaded source files
    temp_upload_dir = "temp_uploads"
    os.makedirs(temp_upload_dir, exist_ok=True)

    # Define a unique directory for this request's output clips
    # This prevents conflicts if multiple users upload at once
    request_id = os.urandom(8).hex() # Generate a random string for uniqueness
    output_clips_sub_dir = os.path.join(CLIPS_OUTPUT_DIR, request_id)
    os.makedirs(output_clips_sub_dir, exist_ok=True)
    logger.info(f"Created output directory for clips: {output_clips_sub_dir}")

    temp_video_path = os.path.join(temp_upload_dir, video_file.filename)
    temp_image_path = os.path.join(temp_upload_dir, image_file.filename)

    all_clip_data: List[Dict[str, Any]] = [] # To store details of each clip including URL

    try:
        # Save the uploaded video file
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        logger.info(f"Saved temporary video to {temp_video_path}")

        # Save the uploaded image file
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        logger.info(f"Saved temporary image to {temp_image_path}")

        # Step 1: Find timestamps where the character is present
        extracted_timestamps = extract_character_clips(
            video_path=temp_video_path,
            character_image_path=temp_image_path,
            tolerance=0.6,
            frames_after_detection=40, # 2 seconds at 30fps
            scale_factor=0.5
        )

        if not extracted_timestamps:
            logger.info("No character presence periods detected, returning empty list.")
            return JSONResponse(content={"message": "No clips found.", "clips": []})

        # Step 2: Cut video clips based on timestamps
        logger.info(f"Attempting to cut {len(extracted_timestamps)} clips...")
        for i, (start_time, end_time) in enumerate(extracted_timestamps):
            # Ensure clip duration is reasonable (e.g., at least 1 second)
            if (end_time - start_time) < 1.0:
                logger.warning(f"Skipping clip {i+1} due to very short duration ({end_time - start_time:.2f}s).")
                continue

            clip_filename = f"clip_{i+1}_{request_id}.mp4" # Unique filename for each clip
            output_clip_path = os.path.join(output_clips_sub_dir, clip_filename)

            try:
                cut_video_clip(temp_video_path, start_time, end_time, output_clip_path)
                
                # Construct URL for the frontend
                # Assuming CLIPS_OUTPUT_DIR is mounted at '/extracted_clips' on the web server
                public_clip_url = f"/extracted_clips/{request_id}/{clip_filename}"
                
                all_clip_data.append({
                    "id": i + 1,
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(end_time - start_time, 2),
                    "url": public_clip_url
                })
            except HTTPException as e:
                # Re-raise FFmpeg errors so they are caught by the outer except
                raise e
            except Exception as e:
                logger.error(f"Failed to cut clip {i+1}: {e}")
                # Continue processing other clips even if one fails, or decide to fail fast
                # For now, we'll continue and just won't include this clip.
                # If a critical error, you might want to re-raise.

        logger.info(f"Successfully generated {len(all_clip_data)} clips.")
        return JSONResponse(content={"message": "Clips found and generated successfully!", "clips": all_clip_data})

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception("An unhandled error occurred during clip finding and generation process.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        # Clean up temporary uploaded files
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            logger.info(f"Cleaned up temporary video: {temp_video_path}")
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            logger.info(f"Cleaned up temporary image: {temp_image_path}")
        
        # Clean up the specific request's output directory if no clips were made or an error occurred
        # Only remove if it's empty after all cleanups, or if error occurred and it's not needed.
        # If you want to keep clips for some time, this cleanup logic needs adjustment.
        # For now, we'll clean up the *entire* request_id directory.
        # if os.path.exists(output_clips_sub_dir) and not all_clip_data: # If no clips generated, remove it
        #     shutil.rmtree(output_clips_sub_dir)
        #     logger.info(f"Cleaned up empty or failed clip directory: {output_clips_sub_dir}")
        elif os.path.exists(output_clips_sub_dir) and all_clip_data:
            logger.info(f"Keeping clips in {output_clips_sub_dir}. Manual cleanup might be needed later if not handled by server lifecycle.")

        # Clean up the main temp_upload_dir only if it's empty
        if os.path.exists(temp_upload_dir) and not os.listdir(temp_upload_dir):
             os.rmdir(temp_upload_dir)
             logger.info(f"Cleaned up empty directory {temp_upload_dir}")