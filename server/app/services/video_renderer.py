"""
Video rendering service for stitching timeline clips into final video.
"""

import os
import subprocess
import tempfile
import uuid
import logging
from typing import List, Dict, Optional
from pathlib import Path
import shlex
import shutil
import json

logger = logging.getLogger(__name__)

async def generate_video_from_image(image_path: str, output_path: str, duration: int = 3, resolution: str = "1280x720"):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", str(duration),
        "-vf", f"scale={resolution},format=yuv420p",
        "-r", "25",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    logger.info(f"Generating video from image: {image_path} -> {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to generate video from image: {result.stderr}")
        raise RuntimeError(result.stderr)

async def generate_video_from_text(text: str, output_path: str, duration: int = 3, resolution: str = "1280x720"):
    # Use Inter.ttf from titan/public/fonts/
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    # Escape comma in font filename for ffmpeg
    font_filename = 'Inter-VariableFont_opsz,wght.ttf'.replace(',', '\\,')
    font_path = os.path.join(project_root, 'client-2', 'public', 'fonts', font_filename)
    safe_text = text.replace(':', '\\:').replace("'", "\\'")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s={resolution}:d={duration}",
        f"-vf", f"drawtext=fontfile={font_path}:text='{safe_text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
        "-r", "25",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    logger.info(f"Generating video from text: '{text}' -> {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to generate video from text: {result.stderr}")
        raise RuntimeError(result.stderr)

async def preprocess_timeline_items(timeline_clips: List[Dict], temp_dir: str) -> List[Dict]:
    processed_clips = []
    clips_dir = os.path.join(os.getcwd(), "generated_clips")
    os.makedirs(clips_dir, exist_ok=True)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    # --- Detect target resolution from first video clip ---
    target_resolution = "1280x720"  # fallback default
    for item in timeline_clips:
        if item.get('type') == 'clip':
            # Try to get the file path for the first video clip
            clip_url = item.get('clip_url', '')
            clip_filename = item.get('clip_filename')
            if not clip_filename and clip_url.startswith('/api/v1/process/clips/'):
                clip_filename = clip_url.split('/')[-1]
            if clip_filename:
                clip_path = os.path.join(clips_dir, clip_filename)
                if os.path.exists(clip_path):
                    # Use ffprobe to get resolution
                    try:
                        cmd = [
                            'ffprobe', '-v', 'error',
                            '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height',
                            '-of', 'csv=p=0',
                            clip_path
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                        w, h = result.stdout.strip().split(',')
                        target_resolution = f"{w}x{h}"
                        break
                    except Exception as e:
                        pass
    # --- End detect target resolution ---
    for idx, item in enumerate(timeline_clips):
        logger.warning(f"[debug] Timeline item {idx}: {item}")
        item_type = item.get('type')
        # Infer type if missing
        if not item_type:
            name = str(item.get('name', ''))
            url = str(item.get('url', ''))
            if any(name.lower().endswith(ext) or url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                item_type = 'image'
                logger.warning(f"[preprocess_timeline_items] Inferred type 'image' for item {idx} from name/url.")
            elif 'text' in item and item['text']:
                item_type = 'text'
                logger.warning(f"[preprocess_timeline_items] Inferred type 'text' for item {idx} from presence of 'text' field.")
            elif 'clip_url' in item and item['clip_url']:
                item_type = 'clip'
                logger.warning(f"[preprocess_timeline_items] Inferred type 'clip' for item {idx} from clip_url.")
        logger.info(f"[preprocess_timeline_items] Processing item {idx}: type={item_type} name={item.get('name')}")
        if item_type == 'clip':
            # Only include required TimelineClip fields
            processed_clips.append({
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
                'clip_filename': item.get('clip_filename', None),
            })
        elif item_type == 'image':
            image_path = item.get('url') or item.get('file_path')
            if not image_path:
                name = str(item.get('name', ''))
                if any(name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    image_path = f"/assets/images/{name.strip().lower()}"
            if image_path and image_path.startswith('/assets/images/'):
                filename = os.path.basename(image_path)
                filename = filename.strip().lower()
                local_path = os.path.join(project_root, 'titan', 'public', 'assets', 'images', filename)
                logger.warning(f"[debug] Checking for image at: {local_path}")
                if os.path.exists(local_path):
                    image_path = local_path
                else:
                    logger.warning(f"[debug] Fallback triggered: {local_path} does not exist. Using fallback black image.")
                    logger.warning(f"[preprocess_timeline_items] Uploaded image file not found: {local_path}. Using fallback black image.")
                    image_path = os.path.join(project_root, 'titan/public/assets/bg', 'black.jpg')
            elif not image_path or not os.path.exists(image_path):
                logger.warning(f"[debug] Fallback triggered: {image_path} does not exist or is missing. Using fallback black image.")
                image_path = os.path.join(project_root, 'titan/public/assets/bg', 'black.jpg')
                logger.warning(f"[preprocess_timeline_items] Image item {idx} missing or invalid. Using fallback black image.")
            duration = int(item.get('duration', 3))
            out_path = os.path.join(temp_dir, f"image_{idx}.mp4")
            await generate_video_from_image(image_path, out_path, duration=duration, resolution=target_resolution)
            filename = os.path.basename(out_path)
            dest_path = os.path.join(clips_dir, filename)
            shutil.copy2(out_path, dest_path)
            logger.info(f"[preprocess_timeline_items] Image segment {idx} generated and copied as {filename}")
            processed_clips.append({
                'timelineId': int(item.get('timelineId', idx)),
                'id': int(item.get('id', idx)),
                'name': str(item.get('name', f'Image {idx+1}')),
                'duration': str(duration),
                'clip_url': f"/api/v1/process/clips/{filename}",
                'clip_filename': filename,
                'thumbnail_url': None,
                'startTime': '0:00',
                'endTime': '0:03',
                'confidence': 1.0,
                'vibe': None,
                'reason': None,
                'scores': None,
            })
        elif item_type == 'text':
            text = item.get('text', item.get('name', ''))
            if not text:
                text = 'Untitled'
                logger.warning(f"[preprocess_timeline_items] Text item {idx} missing 'text' or 'name'. Using fallback 'Untitled'.")
            duration = int(item.get('duration', 3))
            out_path = os.path.join(temp_dir, f"text_{idx}.mp4")
            await generate_video_from_text(text, out_path, duration=duration, resolution=target_resolution)
            filename = os.path.basename(out_path)
            dest_path = os.path.join(clips_dir, filename)
            shutil.copy2(out_path, dest_path)
            logger.info(f"[preprocess_timeline_items] Text segment {idx} generated and copied as {filename}")
            processed_clips.append({
                'timelineId': int(item.get('timelineId', idx)),
                'id': int(item.get('id', idx)),
                'name': str(item.get('name', f'Text {idx+1}')),
                'duration': str(duration),
                'clip_url': f"/api/v1/process/clips/{filename}",
                'clip_filename': filename,
                'thumbnail_url': None,
                'startTime': '0:00',
                'endTime': '0:03',
                'confidence': 1.0,
                'vibe': None,
                'reason': None,
                'scores': None,
            })
        else:
            logger.warning(f"[preprocess_timeline_items] Unknown timeline item type: {item_type}, skipping.")
    return processed_clips

# Helper to robustly parse durations in 'mm:ss' or seconds format

def parse_duration(duration):
    if isinstance(duration, (int, float)):
        return float(duration)
    if isinstance(duration, str):
        if ':' in duration:
            parts = duration.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return int(minutes) * 60 + float(seconds)
        return float(duration)
    raise ValueError(f"Invalid duration: {duration}")

class VideoRenderer:
    """
    Service for rendering final videos by stitching timeline clips.
    """
    
    def __init__(self, output_base_dir: Optional[str] = None):
        if output_base_dir is None:
            # Default to rendered_videos directory in current working directory
            self.output_base_dir = os.path.join(os.getcwd(), "rendered_videos")
            os.makedirs(self.output_base_dir, exist_ok=True)
        else:
            self.output_base_dir = output_base_dir
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self):
        """Verify ffmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True, timeout=5)
            logger.info("✅ ffmpeg is available for video rendering")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("⚠️ ffmpeg not found or not working")
            raise RuntimeError("ffmpeg is required for video rendering")
    
    async def render_timeline_video(self, 
                                  timeline_clips: List[Dict],
                                  bgm_file_path: Optional[str] = None,
                                  sfx_list: Optional[List[Dict]] = None,
                                  output_format: str = "mp4",
                                  project_name: str = "final_video",
                                  bgm_regions: Optional[List[Dict[str, float]]] = None) -> Dict:
        """
        Render timeline clips into a final video.
        Args:
            timeline_clips: List of clips with file paths and metadata
            bgm_file_path: Optional background music file path
            sfx_list: Optional list of sound effects, each as {"path": str, "delay_ms": int}
            output_format: Output video format (mp4, mov, etc.)
            project_name: Project name for output filename
            bgm_regions: List of {start, duration} dicts for selective BGM (as a hint)
        Returns:
            Dict with rendered video info
        """
        if not timeline_clips:
            raise ValueError("No clips provided for rendering")
        render_id = str(uuid.uuid4())[:8]
        output_filename = f"{project_name}_{render_id}_final.{output_format}"
        output_path = os.path.join(self.output_base_dir, output_filename)
        logger.info(f"🎬 Starting video rendering: {len(timeline_clips)} clips")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                processed_clips = await preprocess_timeline_items(timeline_clips, temp_dir)
                # --- Compute mute regions for BGM (where timeline item is a video/clip) ---
                mute_regions = []
                play_regions = []
                current_time = 0.0
                for item in processed_clips:
                    duration = parse_duration(item.get('duration', 3))
                    orig_type = None
                    if 'type' in item:
                        orig_type = item['type']
                    if orig_type == 'clip':
                        mute_regions.append({'start': current_time, 'end': current_time + duration})
                    elif orig_type in ('image', 'text') or (not orig_type and item.get('text')):
                        play_regions.append({'start': current_time, 'end': current_time + duration})
                    current_time += duration
                logger.info(f"[BGM] Computed mute regions for BGM: {mute_regions}")
                logger.info(f"[BGM] Computed play regions for BGM: {play_regions}")
                concat_file_path = await self._prepare_concat_list(processed_clips, temp_dir)
                temp_video_path = os.path.join(temp_dir, "concatenated_video.mp4")
                await self._concatenate_clips(concat_file_path, temp_video_path)
                # --- Ensure audio stream exists ---
                if not await self._has_audio_stream(temp_video_path):
                    logger.warning('[audio-fix] No audio stream detected, adding silent audio track...')
                    temp_with_audio = os.path.join(temp_dir, "concatenated_with_audio.mp4")
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', temp_video_path,
                        '-f', 'lavfi',
                        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                        '-shortest',
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        temp_with_audio
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.error(f"[audio-fix] Failed to add silent audio: {result.stderr}")
                        raise RuntimeError(f"Failed to add silent audio: {result.stderr}")
                    temp_video_path = temp_with_audio
                # --- End ensure audio stream ---
                # Step 3: Add BGM and SFX if provided
                if (bgm_file_path and os.path.exists(bgm_file_path)):
                    final_video_path = await self._add_bgm_and_sfx_with_mute(
                        temp_video_path, bgm_file_path, sfx_list or [], output_path, mute_regions
                    )
                else:
                    await self._finalize_video(temp_video_path, output_path)
                if not os.path.exists(output_path):
                    raise RuntimeError("Output video file was not created")
                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    raise RuntimeError("Output video file is empty")
                duration = await self._get_video_duration(output_path)
                return {
                    'render_id': render_id,
                    'filename': output_filename,
                    'file_path': output_path,
                    'file_size': file_size,
                    'duration': duration,
                    'clips_count': len(processed_clips),
                    'has_bgm': bgm_file_path is not None,
                    'has_sfx': bool(sfx_list),
                    'url': f"/api/v1/process/rendered-videos/{output_filename}",
                    'status': 'success'
                }
        except Exception as e:
            logger.error(f"Video rendering failed: {e}")
            raise RuntimeError(f"Video rendering failed: {str(e)}")
    
    async def _prepare_concat_list(self, timeline_clips: List[Dict], temp_dir: str) -> str:
        """Prepare ffmpeg concat list file."""
        concat_file_path = os.path.join(temp_dir, "concat_list.txt")
        
        # Resolve clip file paths
        clips_dir = os.path.join(os.getcwd(), "generated_clips")
        
        with open(concat_file_path, 'w') as f:
            for i, clip in enumerate(timeline_clips):
                # Get clip filename from clip data
                clip_filename = clip.get('clip_filename')
                if not clip_filename:
                    # Try to construct from clip_url
                    clip_url = clip.get('clip_url', '')
                    if clip_url.startswith('/api/v1/process/clips/'):
                        clip_filename = clip_url.split('/')[-1]
                    else:
                        raise ValueError(f"Cannot determine filename for clip {i}")
                
                clip_path = os.path.join(clips_dir, clip_filename)
                
                if not os.path.exists(clip_path):
                    raise FileNotFoundError(f"Clip file not found: {clip_path}")
                
                # Write to concat file (escape path for ffmpeg)
                escaped_path = clip_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
                
                logger.info(f"Added clip {i+1}: {clip_filename}")
        
        return concat_file_path
    
    async def _concatenate_clips(self, concat_file_path: str, output_path: str):
        """Concatenate video clips using a robust ffmpeg filter_complex command."""
        try:
            with open(concat_file_path, 'r') as f:
                concat_contents = f.read()
        except Exception as e:
            logger.error(f"[debug] Failed to read concat list file: {e}")
            raise
        file_paths = [line.split("file '")[1].split("'")[0] for line in concat_contents.strip().split('\n') if line.startswith("file '")]

        def get_video_props(path):
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,pix_fmt', '-of', 'json', path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stream = json.loads(result.stdout)['streams'][0]
            fr = stream['r_frame_rate']
            num, den = fr.split('/') if '/' in fr else (fr, 1)
            return int(stream['width']), int(stream['height']), float(num) / float(den), stream['pix_fmt']

        def has_audio(path):
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'json', path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            try:
                return len(json.loads(result.stdout).get('streams', [])) > 0
            except json.JSONDecodeError:
                return False

        target_width, target_height, target_fps, target_pix_fmt = get_video_props(file_paths[0])
        logger.info(f"[fix_concat] Target properties: {target_width}x{target_height}, {target_fps:.2f}fps, {target_pix_fmt}")

        with tempfile.TemporaryDirectory() as fix_dir:
            fixed_files = []
            audio_flags = []
            for i, in_path in enumerate(file_paths):
                audio_flags.append(has_audio(in_path))
                w, h, fps, pix_fmt = get_video_props(in_path)
                needs_fix = (w != target_width) or (h != target_height) or (abs(fps - target_fps) > 0.01) or (pix_fmt != target_pix_fmt)
                out_path = os.path.join(fix_dir, f"fixed_{i}.mp4")
                
                cmd_fix = [
                    'ffmpeg', '-y', '-i', in_path,
                    '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps}',
                    '-pix_fmt', target_pix_fmt,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
                ]
                if audio_flags[i]:
                    cmd_fix.extend(['-c:a', 'aac', '-b:a', '192k'])
                else:
                    cmd_fix.extend(['-an'])
                cmd_fix.append(out_path)
                
                logger.info(f"[fix_concat] Processing segment {i}: {'Re-encoding' if needs_fix else 'Copying'}")
                result = subprocess.run(cmd_fix, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"[fix_concat] Failed to process {in_path}: {result.stderr}")
                    raise RuntimeError(f"Failed to process {in_path}: {result.stderr}")
                fixed_files.append(out_path)

            input_args = []
            video_chain = ""
            audio_chain = ""
            num_audio_inputs = 0

            for i, path in enumerate(fixed_files):
                input_args.extend(['-i', path])
                video_chain += f'[{i}:v:0]'
                if audio_flags[i]:
                    audio_chain += f'[{i}:a:0]'
                    num_audio_inputs += 1

            if num_audio_inputs == 0:
                # No audio streams at all, create silent video
                filter_complex = f"{video_chain}concat=n={len(fixed_files)}:v=1:a=0[v]"
                map_args = ['-map', '[v]']
                audio_codec_args = ['-an']
            else:
                # Some streams have audio, create silent streams for those that don't
                final_audio_chain = ""
                audio_input_idx = 0
                for i in range(len(fixed_files)):
                    if audio_flags[i]:
                        final_audio_chain += f'[{audio_input_idx}:a:0]'
                        audio_input_idx += 1
                    else:
                        # Create a silent audio stream for the duration of the video segment
                        duration = await self._get_video_duration(fixed_files[i])
                        input_args.extend(['-f', 'lavfi', '-t', str(duration), '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100'])
                        final_audio_chain += f'[{len(fixed_files) + i - audio_input_idx}:a:0]'

                filter_complex = f"{video_chain}concat=n={len(fixed_files)}:v=1:a=0[v];{final_audio_chain}concat=n={len(fixed_files)}:v=0:a=1[a]"
                map_args = ['-map', '[v]', '-map', '[a]']
                audio_codec_args = ['-c:a', 'aac', '-b:a', '192k']

            cmd = [
                'ffmpeg', '-y', *input_args,
                '-filter_complex', filter_complex,
                *map_args,
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                *audio_codec_args,
                '-shortest', output_path
            ]

            logger.warning(f"[debug] ffmpeg filter_complex concat command: {' '.join(shlex.quote(s) for s in cmd)}")
            logger.info("🔗 Concatenating video clips with filter_complex...")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
                logger.info("✅ Video clips concatenated successfully (filter_complex)")
            except subprocess.CalledProcessError as e:
                logger.error(f"ffmpeg filter_complex concat failed: {e.stderr}")
                raise RuntimeError(f"Video concatenation failed: {e.stderr}")
            except subprocess.TimeoutExpired:
                logger.error("ffmpeg filter_complex concat timed out")
                raise RuntimeError("Video concatenation timed out")

    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            probe_data = json.loads(result.stdout)
            duration = float(probe_data.get('format', {}).get('duration', 0))
            return duration
        except Exception as e:
            logger.warning(f"Failed to get video duration: {e}")
            return 0.0

    async def _add_bgm_and_sfx(self, video_path: str, bgm_path: Optional[str], sfx_list: list, output_path: str) -> str:
        input_args = ['-i', video_path]
        filter_parts = []
        amix_inputs = '[0:a]'
        idx = 1
        # Add BGM if provided
        if bgm_path and os.path.exists(bgm_path):
            input_args += ['-i', bgm_path]
            filter_parts.append(f'[{idx}]aloop=loop=-1:size=2e+09,asetpts=N/SR/TB[bgm]')
            amix_inputs += '[bgm]'
            idx += 1
        # Add SFX
        for i, sfx in enumerate(sfx_list):
            sfx_path = sfx.get('path')
            delay = int(sfx.get('delay_ms', 0))
            if not sfx_path or not os.path.exists(sfx_path):
                continue
            input_args += ['-i', sfx_path]
            filter_parts.append(f'[{idx}]adelay={delay}|{delay}[sfx{i}]')
            amix_inputs += f'[sfx{i}]'
            idx += 1
        n_inputs = amix_inputs.count('[')
        filter_parts.append(f'{amix_inputs}amix=inputs={n_inputs}:duration=longest[aout]')
        filter_complex = ';'.join(filter_parts)
        cmd = [
            'ffmpeg', '-y',
            *input_args,
            '-filter_complex', filter_complex,
            '-map', '0:v:0',
            '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-b:a', '128k',
            output_path
        ]
        logger.info("🎵 Adding BGM and SFX (if any)...")
        logger.warning(f"[debug] ffmpeg BGM+SFX command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=240,
                check=True
            )
            logger.info("✅ BGM and SFX added successfully")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg BGM+SFX addition failed: {e.stderr}")
            raise RuntimeError(f"BGM+SFX addition failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg BGM+SFX addition timed out")
            raise RuntimeError("BGM+SFX addition timed out")
    
    async def _add_bgm_and_sfx_with_mute(self, video_path: str, bgm_path: Optional[str], sfx_list: list, output_path: str, mute_regions: list) -> str:
        """
        Add BGM with audio ducking: BGM is lowered during video clips and at full volume otherwise.
        """
        input_args = ['-i', video_path]
        
        if not (bgm_path and os.path.exists(bgm_path)):
            # No BGM, just ensure the output file exists in the correct format.
            cmd_copy = ['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path]
            subprocess.run(cmd_copy, check=True, capture_output=True, text=True)
            return output_path

        input_args.extend(['-stream_loop', '-1', '-i', bgm_path])

        filter_parts = []
        
        # If there are clips with audio, set up ducking
        if mute_regions:
            # Ducking expression: sets volume to 0.2 during clip regions, 1.0 otherwise.
            ducking_expr = '+'.join([f'between(t,{r["start"]},{r["end"]})' for r in mute_regions])
            volume_filter = f"[1:a]volume=if({ducking_expr}, 0.2, 1.0)[bgm_ducked]"
            filter_parts.append(volume_filter)
            
            # Mix the original audio with the ducked BGM
            mix_filter = f"[0:a][bgm_ducked]amerge=inputs=2[aout]"
            filter_parts.append(mix_filter)
            map_audio = '[aout]'
        else:
            # No clips, just mix main audio (which should be silent) with BGM at full volume
            mix_filter = "[0:a][1:a]amerge=inputs=2[aout]"
            filter_parts.append(mix_filter)
            map_audio = '[aout]'

        filter_complex = ';'.join(filter_parts)
        
        cmd = [
            'ffmpeg', '-y',
            *input_args,
            '-filter_complex', filter_complex,
            '-map', '0:v:0',
            '-map', f'{map_audio}',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-b:a', '192k',
            output_path
        ]
        
        logger.info("🎵 Adding BGM with audio ducking...")
        logger.warning(f"[debug] ffmpeg audio ducking command: {' '.join(shlex.quote(s) for s in cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=True
            )
            logger.info("✅ BGM with audio ducking added successfully")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg audio ducking failed: {e.stderr}")
            raise RuntimeError(f"BGM ducking failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg audio ducking timed out")
            raise RuntimeError("BGM ducking timed out")

    async def _finalize_video(self, temp_video_path: str, output_path: str):
        """Finalize video with optimization."""
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video_path,
            '-c:v', 'copy',    # Re-encode with H.264
            '-c:a', 'copy',        # Re-encode audio with AAC
            '-movflags', '+faststart',  # Web optimization
            output_path
        ]
        logger.info("🎞️ Finalizing video...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
                check=True
            )
            logger.info("✅ Video finalized successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg finalization failed: {e.stderr}")
            raise RuntimeError(f"Video finalization failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg finalization timed out")
            raise RuntimeError("Video finalization timed out")

    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            probe_data = json.loads(result.stdout)
            duration = float(probe_data.get('format', {}).get('duration', 0))
            return duration
        except Exception as e:
            logger.warning(f"Failed to get video duration: {e}")
            return 0.0

    async def _has_audio_stream(self, video_path: str) -> bool:
        """Check if a video file has an audio stream."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'a',
            '-show_entries', 'stream=index',
            '-of', 'json',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            info = json.loads(result.stdout)
            return 'streams' in info and len(info['streams']) > 0
        except Exception:
            return False


class VideoRenderingManager:
    """
    High-level manager for video rendering workflow.
    """
    def __init__(self, video_renderer: VideoRenderer):
        self.video_renderer = video_renderer
    async def render_project_video(self, 
                                 timeline_data: Dict,
                                 project_name: str = "project") -> Dict:
        """
        Render final video from project timeline data.
        Args:
            timeline_data: Dict containing timeline_clips and optional bgm_path and sfx_list and bgm_regions
            project_name: Name for the output video file
        Returns:
            Dict with render result information
        """
        timeline_clips = timeline_data.get('timeline_clips', [])
        bgm_path = timeline_data.get('bgm_path')
        sfx_list = timeline_data.get('sfx_list', [])
        bgm_regions = timeline_data.get('bgm_regions', None)
        if not timeline_clips:
            raise ValueError("No clips in timeline to render")
        try:
            render_result = await self.video_renderer.render_timeline_video(
                timeline_clips=timeline_clips,
                bgm_file_path=bgm_path,
                sfx_list=sfx_list,
                project_name=project_name,
                bgm_regions=bgm_regions
            )
            logger.info(f"✅ Project video rendered successfully: {render_result['filename']}")
            return render_result
        except Exception as e:
            logger.error(f"Project video rendering failed: {e}")
            raise RuntimeError(f"Project video rendering failed: {str(e)}")