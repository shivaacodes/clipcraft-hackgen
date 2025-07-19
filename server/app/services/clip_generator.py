"""
Video clip generation service using ffmpeg.
Generates actual video clips from timestamps.
"""

import os
import subprocess
import tempfile
import uuid
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ClipGenerator:
    """
    Service for generating video clips using ffmpeg.
    """
    
    def __init__(self, output_base_dir: Optional[str] = None):
        if output_base_dir is None:
            # Default to generated_clips directory in current working directory
            self.output_base_dir = os.path.join(os.getcwd(), "generated_clips")
            os.makedirs(self.output_base_dir, exist_ok=True)
        else:
            self.output_base_dir = output_base_dir
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self):
        """Verify ffmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True, timeout=5)
            logger.info("✅ ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("⚠️ ffmpeg not found or not working")
            raise RuntimeError("ffmpeg is required for clip generation")
    
    async def generate_clips_from_analysis(self, 
                                         video_path: str,
                                         vibe_analysis_result: Dict,
                                         max_clips: int = 3,  # Increased for shorter clips
                                         fast_mode: bool = True) -> List[Dict]:  # Add fast mode
        """
        Generate actual video clips from vibe analysis results.
        
        Args:
            video_path: Path to source video file
            vibe_analysis_result: Result from Claude vibe analysis
            max_clips: Maximum number of clips to generate
            fast_mode: If True, use faster but lower quality settings
            
        Returns:
            List of generated clip info with file paths
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Source video not found: {video_path}")
        
        vibe_analysis = vibe_analysis_result.get('vibe_analysis', {})
        top_clips = vibe_analysis.get('top_clips', [])
        
        if not top_clips:
            logger.warning("No clips found in vibe analysis")
            return []
        
        # Limit number of clips to generate
        clips_to_generate = top_clips[:max_clips]
        generated_clips = []
        
        logger.info(f"🎬 Generating {len(clips_to_generate)} video clips...")
        
        for i, clip_data in enumerate(clips_to_generate):
            try:
                clip_info = await self._generate_single_clip(
                    video_path, clip_data, i + 1, fast_mode
                )
                if clip_info:
                    generated_clips.append(clip_info)
                    logger.info(f"✅ Generated clip {i+1}: {clip_info['filename']}")
            except Exception as e:
                logger.error(f"❌ Failed to generate clip {i+1}: {e}")
                continue
        
        return generated_clips
    
    async def _generate_single_clip(self, 
                                  video_path: str, 
                                  clip_data: Dict, 
                                  clip_number: int,
                                  fast_mode: bool = True) -> Optional[Dict]:
        """Generate a single video clip."""
        
        start_time = clip_data.get('start_time', 0)
        end_time = clip_data.get('end_time', 0)
        duration = end_time - start_time
        
        # Validate clip duration (optimized for shorter clips)
        if duration < 2 or duration > 15:  # 2 seconds to 15 seconds
            logger.warning(f"Invalid clip duration: {duration}s")
            return None
        
        # Generate unique filename
        clip_id = str(uuid.uuid4())[:8]
        clip_filename = f"clip_{clip_number}_{clip_id}_{int(start_time)}s-{int(end_time)}s.mp4"
        output_path = os.path.join(self.output_base_dir, clip_filename)
        
        # Generate thumbnail first
        thumbnail_filename = f"thumb_{clip_number}_{clip_id}_{int(start_time)}s.jpg"
        thumbnail_path = os.path.join(self.output_base_dir, thumbnail_filename)
        
        # Create thumbnail at middle of clip (optimized)
        thumbnail_time = start_time + (duration / 2)
        thumb_cmd = [
            'ffmpeg', '-y',
            '-ss', str(thumbnail_time),  # Seek before input for speed
            '-i', video_path,
            '-vframes', '1',  # Extract 1 frame
            '-vf', 'scale=320:180',  # Resize to 320x180
            '-f', 'image2',  # Force image format
            '-q:v', '5',  # Reduced quality for speed (5 vs 2)
            thumbnail_path
        ]
        
        try:
            subprocess.run(thumb_cmd, capture_output=True, check=True, timeout=5)  # Reduced timeout
            logger.info(f"📸 Generated thumbnail: {thumbnail_filename}")
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            thumbnail_path = None
            thumbnail_filename = None

        # Generate clip using ffmpeg with conditional settings
        if fast_mode:
            # Ultra-fast mode for development
            cmd = [
                'ffmpeg', '-y',  # Overwrite output files
                '-ss', str(start_time),  # Seek to start time BEFORE input (faster)
                '-i', video_path,  # Input file
                '-t', str(duration),  # Duration
                '-c:v', 'copy',  # Copy video stream (no re-encoding, fastest!)
                '-c:a', 'copy',  # Copy audio stream (no re-encoding)
                '-avoid_negative_ts', 'make_zero',  # Handle timing issues
                output_path
            ]
        else:
            # Higher quality mode
            cmd = [
                'ffmpeg', '-y',  # Overwrite output files
                '-i', video_path,  # Input file first for frame-accurate seek
                '-ss', str(start_time),  # Seek after input for accuracy
                '-t', str(duration),  # Duration
                '-c:v', 'libx264',  # Video codec
                '-c:a', 'aac',  # Re-encode audio for accurate cuts
                '-b:a', '128k',  # Set audio bitrate
                '-preset', 'ultrafast',  # Fastest encoding preset
                '-crf', '28',  # Lower quality for speed
                '-avoid_negative_ts', 'make_zero',  # Handle timing issues
                output_path
            ]
        
        try:
            # Run ffmpeg command
            # Adjust timeout based on mode
            timeout = 5 if fast_mode else 15  # Much faster timeout for copy mode
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=True
            )
            
            # Verify output file was created
            if not os.path.exists(output_path):
                logger.error(f"Output file not created: {output_path}")
                return None
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                logger.error(f"Generated clip is empty: {output_path}")
                os.remove(output_path)
                return None
            
            return {
                'clip_id': clip_id,
                'filename': clip_filename,
                'file_path': output_path,
                'thumbnail_filename': thumbnail_filename,
                'thumbnail_path': thumbnail_path,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'file_size': file_size,
                'title': clip_data.get('title', f'Clip {clip_number}'),
                'vibe': clip_data.get('vibe', ''),
                'scores': clip_data.get('scores', {}),
                'reason': clip_data.get('reason', ''),
                'url': f"/api/v1/process/clips/{clip_filename}",  # URL for frontend access
                'thumbnail_url': f"/api/v1/process/clips/{thumbnail_filename}" if thumbnail_filename else None
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg timed out")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating clip: {e}")
            return None
    
    def cleanup_clips(self, clip_paths: List[str]):
        """Clean up generated clip files."""
        for path in clip_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"🗑️ Cleaned up clip: {path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {path}: {e}")
    
    def get_clip_info(self, clip_path: str) -> Optional[Dict]:
        """Get information about a generated clip."""
        if not os.path.exists(clip_path):
            return None
        
        try:
            # Use ffprobe to get video info
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                clip_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            probe_data = json.loads(result.stdout)
            
            format_info = probe_data.get('format', {})
            video_stream = next(
                (s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video'),
                {}
            )
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'bitrate': int(format_info.get('bit_rate', 0))
            }
            
        except Exception as e:
            logger.error(f"Failed to get clip info: {e}")
            return None


class ClipGenerationManager:
    """
    High-level manager for clip generation workflow.
    """
    
    def __init__(self, clip_generator: ClipGenerator):
        self.clip_generator = clip_generator
    
    async def generate_clips_from_pipeline_result(self, 
                                                pipeline_result: Dict,
                                                source_video_path: str,
                                                max_clips: int = 2,
                                                fast_mode: bool = True) -> Dict:
        """
        Generate clips from complete pipeline result.
        Args:
            pipeline_result: Complete result from video processing pipeline
            source_video_path: Path to original video file
            max_clips: Maximum clips to generate
        Returns:
            Updated pipeline result with generated clip file paths
        """
        try:
            vibe_analysis = pipeline_result.get('vibe_analysis', {})
            fallback_used = False
            top_clips = []
            # Fallback if no vibe_analysis or no top_clips
            if not vibe_analysis or not vibe_analysis.get('vibe_analysis', {}).get('top_clips'):
                logger.warning("No vibe analysis or top_clips found, using fallback evenly spaced clips.")
                fallback_used = True
                # Use transcription/chunks info to select evenly spaced highlights
                transcription = pipeline_result.get('transcription', {})
                chunks = transcription.get('chunks', [])
                # Only use successful chunks with valid transcription
                valid_chunks = [c for c in chunks if c.get('success') and c.get('transcription', {}).get('text')]
                if not valid_chunks:
                    logger.error("No valid chunks available for fallback clip generation.")
                    pipeline_result['generated_clips'] = {
                        'total_generated': 0,
                        'clips': [],
                        'status': 'failed',
                        'error': 'No valid chunks for fallback clip generation.'
                    }
                    return pipeline_result
                # Evenly spaced selection
                step = max(1, len(valid_chunks) // max_clips)
                selected_chunks = [valid_chunks[i] for i in range(0, len(valid_chunks), step)][:max_clips]
                # Build pseudo-top_clips for fallback
                for c in selected_chunks:
                    start_time = c.get('start_time', 0)
                    end_time = c.get('end_time', 0)
                    top_clips.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'title': f'Highlight {int(start_time)}s-{int(end_time)}s',
                        'reason': 'Evenly spaced fallback highlight',
                        'vibe': '',
                        'scores': {},
                    })
                # Wrap in fake vibe_analysis for downstream compatibility
                vibe_analysis = {'vibe_analysis': {'top_clips': top_clips}}
            # Generate actual video clips
            generated_clips = await self.clip_generator.generate_clips_from_analysis(
                source_video_path, vibe_analysis, max_clips, fast_mode
            )
            # Update the pipeline result with generated clip info
            if generated_clips:
                # Update top_clips with file paths
                vibe_result = vibe_analysis.get('vibe_analysis', {})
                top_clips = vibe_result.get('top_clips', [])
                for i, generated_clip in enumerate(generated_clips):
                    if i < len(top_clips):
                        top_clips[i].update({
                            'clip_file_path': generated_clip['file_path'],
                            'clip_filename': generated_clip['filename'],
                            'clip_url': generated_clip['url'],
                            'clip_id': generated_clip['clip_id'],
                            'file_size': generated_clip['file_size'],
                            'thumbnail_url': generated_clip.get('thumbnail_url'),
                            'thumbnail_filename': generated_clip.get('thumbnail_filename')
                        })
                # Add summary of generated clips
                pipeline_result['generated_clips'] = {
                    'total_generated': len(generated_clips),
                    'clips': generated_clips,
                    'status': 'success' if not fallback_used else 'fallback',
                    'message': 'Fallback used: evenly spaced highlights.' if fallback_used else 'success'
                }
                # --- FIX: Also assign fallback clips to top_clips for frontend ---
                if fallback_used:
                    # If top_clips is empty or missing, set it to generated_clips
                    if 'vibe_analysis' in pipeline_result and 'vibe_analysis' in pipeline_result['vibe_analysis']:
                        pipeline_result['vibe_analysis']['vibe_analysis']['top_clips'] = [
                            {
                                'title': c.get('title', ''),
                                'start_time': c.get('start_time', 0),
                                'end_time': c.get('end_time', 0),
                                'duration': c.get('duration', 0),
                                'clip_url': c.get('url', c.get('clip_url', '')),
                                'thumbnail_url': c.get('thumbnail_url', ''),
                                'scores': c.get('scores', {}),
                                'reason': c.get('reason', ''),
                                'vibe': c.get('vibe', ''),
                                'rank': c.get('rank', None),
                                'clip_filename': c.get('filename', ''),
                                'thumbnail_filename': c.get('thumbnail_filename', ''),
                                'file_size': c.get('file_size', None)
                            }
                            for c in generated_clips
                        ]
            else:
                pipeline_result['generated_clips'] = {
                    'total_generated': 0,
                    'clips': [],
                    'status': 'no_clips_generated',
                    'message': 'No clips could be generated from the analysis or fallback.'
                }
            return pipeline_result
        except Exception as e:
            logger.error(f"Error in clip generation workflow: {e}")
            pipeline_result['generated_clips'] = {
                'total_generated': 0,
                'clips': [],
                'status': 'failed',
                'error': str(e)
            }
            return pipeline_result