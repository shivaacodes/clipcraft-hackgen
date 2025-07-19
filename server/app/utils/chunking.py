"""
Video chunking utilities for optimal transcription and analysis.
This module implements intelligent video chunking algorithms.
"""

import os
import math
import subprocess
import tempfile
from typing import List, Dict, Tuple, Optional
from moviepy.editor import VideoFileClip
import numpy as np
from pathlib import Path

class VideoChunker:
    """
    Advanced video chunking with multiple strategies for optimal transcription.
    """
    def __init__(self, 
                 chunk_duration: int = 8,  # seconds (longer for better context)
                 overlap_duration: int = 1,  # seconds for context
                 min_chunk_duration: int = 3,  # minimum chunk size (lowered for precision)
                 max_chunk_duration: int = 10):  # maximum chunk size
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.min_chunk_duration = min_chunk_duration
        self.max_chunk_duration = max_chunk_duration
    
    def chunk_video_by_time(self, video_path: str, output_dir: str) -> List[Dict]:
        """
        Chunk video by fixed time intervals with overlap for context.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save chunks
            
        Returns:
            List of chunk metadata dictionaries
        """
        chunks = []
        
        # Get video info using moviepy
        with VideoFileClip(video_path) as video:
            duration = video.duration
            
        # Calculate number of chunks (no artificial limit)
        effective_chunk_duration = self.chunk_duration - self.overlap_duration
        num_chunks = math.ceil(duration / effective_chunk_duration)

        for i in range(num_chunks):
            start_time = max(0, i * effective_chunk_duration - self.overlap_duration)
            end_time = min(duration, start_time + self.chunk_duration)

            # Skip chunks that are too short
            if end_time - start_time < self.min_chunk_duration:
                continue

            chunk_filename = f"chunk_{i:03d}_{int(start_time)}_{int(end_time)}.wav"
            chunk_path = os.path.join(output_dir, chunk_filename)

            # Extract audio chunk using ffmpeg
            self._extract_audio_chunk(video_path, chunk_path, start_time, end_time)

            chunks.append({
                'id': i,
                'filename': chunk_filename,
                'path': chunk_path,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'overlap_start': i > 0,
                'overlap_end': end_time < duration
            })

        return chunks
    
    def chunk_video_by_scene(self, video_path: str, output_dir: str, 
                           scene_threshold: float = 0.3) -> List[Dict]:
        """
        Chunk video by scene detection for more natural breaks.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save chunks
            scene_threshold: Sensitivity for scene change detection
            
        Returns:
            List of chunk metadata dictionaries
        """
        chunks = []
        
        # Use ffmpeg's scene detection
        scene_times = self._detect_scenes(video_path, scene_threshold)
        
        with VideoFileClip(video_path) as video:
            duration = video.duration
            
        # Add start and end times
        scene_times = [0.0] + scene_times + [duration]
        scene_times = sorted(list(set(scene_times)))  # Remove duplicates and sort
        
        # Group scenes into chunks
        current_chunk_start = 0.0
        chunk_id = 0
        
        for i in range(1, len(scene_times)):
            current_duration = scene_times[i] - current_chunk_start
            
            # If chunk is getting too long or we've reached a natural break
            if (current_duration >= self.chunk_duration or 
                scene_times[i] == duration):
                
                # Ensure minimum duration
                if current_duration >= self.min_chunk_duration:
                    chunk_filename = f"scene_chunk_{chunk_id:03d}_{int(current_chunk_start)}_{int(scene_times[i])}.wav"
                    chunk_path = os.path.join(output_dir, chunk_filename)
                    
                    # Extract audio chunk
                    self._extract_audio_chunk(video_path, chunk_path, 
                                            current_chunk_start, scene_times[i])
                    
                    chunks.append({
                        'id': chunk_id,
                        'filename': chunk_filename,
                        'path': chunk_path,
                        'start_time': current_chunk_start,
                        'end_time': scene_times[i],
                        'duration': scene_times[i] - current_chunk_start,
                        'scene_based': True,
                        'scene_break': True
                    })
                    
                    chunk_id += 1
                    current_chunk_start = scene_times[i]
                    
        return chunks
    
    def chunk_video_adaptive(self, video_path: str, output_dir: str) -> List[Dict]:
        """
        Adaptive chunking that combines time-based and scene-based approaches.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save chunks
            
        Returns:
            List of chunk metadata dictionaries
        """
        # First try scene-based chunking
        scene_chunks = self.chunk_video_by_scene(video_path, output_dir)
        
        # If scene detection produces very long chunks, fall back to time-based
        refined_chunks = []
        chunk_id = 0
        
        for chunk in scene_chunks:
            if chunk['duration'] <= self.max_chunk_duration:
                chunk['id'] = chunk_id
                refined_chunks.append(chunk)
                chunk_id += 1
            else:
                # Split long scene chunks using time-based approach
                sub_chunks = self._split_long_chunk(
                    video_path, output_dir, chunk, chunk_id
                )
                refined_chunks.extend(sub_chunks)
                chunk_id += len(sub_chunks)
                
        return refined_chunks
    
    def _extract_audio_chunk(self, video_path: str, output_path: str, 
                           start_time: float, end_time: float):
        """Extract audio chunk using ffmpeg."""
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite output files
            '-i', video_path,
            '-ss', str(start_time),
            '-t', str(end_time - start_time),
            '-vn',  # no video
            '-acodec', 'pcm_s16le',  # uncompressed audio for better quality
            '-ar', '16000',  # 16kHz sample rate (optimal for whisper)
            '-ac', '1',  # mono audio
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio chunk: {e}")
            raise
    
    def _detect_scenes(self, video_path: str, threshold: float = 0.3) -> List[float]:
        """Detect scene changes using ffmpeg's scene detection."""
        cmd = [
            'ffmpeg', '-i', video_path,
            '-filter:v', f'select=gt(scene\\,{threshold})',
            '-f', 'null', '-'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Parse scene detection output
            scene_times = []
            for line in result.stderr.split('\n'):
                if 'pts_time:' in line:
                    try:
                        time_str = line.split('pts_time:')[1].split()[0]
                        scene_times.append(float(time_str))
                    except (IndexError, ValueError):
                        continue
            return scene_times
        except subprocess.CalledProcessError:
            return []  # Fall back to time-based chunking
    
    def _split_long_chunk(self, video_path: str, output_dir: str, 
                         long_chunk: Dict, start_id: int) -> List[Dict]:
        """Split a long chunk into smaller time-based chunks."""
        chunks = []
        start_time = long_chunk['start_time']
        end_time = long_chunk['end_time']
        duration = end_time - start_time
        
        num_sub_chunks = math.ceil(duration / self.chunk_duration)
        
        for i in range(num_sub_chunks):
            sub_start = start_time + (i * self.chunk_duration)
            sub_end = min(end_time, sub_start + self.chunk_duration)
            
            if sub_end - sub_start < self.min_chunk_duration:
                continue
                
            chunk_filename = f"adaptive_chunk_{start_id + i:03d}_{int(sub_start)}_{int(sub_end)}.wav"
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            self._extract_audio_chunk(video_path, chunk_path, sub_start, sub_end)
            
            chunks.append({
                'id': start_id + i,
                'filename': chunk_filename,
                'path': chunk_path,
                'start_time': sub_start,
                'end_time': sub_end,
                'duration': sub_end - sub_start,
                'adaptive': True,
                'parent_chunk': long_chunk['id']
            })
            
        return chunks
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get comprehensive video information."""
        try:
            with VideoFileClip(video_path) as video:
                return {
                    'duration': video.duration,
                    'fps': video.fps,
                    'size': video.size,
                    'audio_fps': video.audio.fps if video.audio else None,
                    'estimated_chunks': math.ceil(video.duration / self.chunk_duration)
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}


class ChunkingStrategy:
    """Factory for different chunking strategies."""
    
    @staticmethod
    def create_chunker(strategy: str = "adaptive", **kwargs) -> VideoChunker:
        """
        Create a video chunker with specified strategy.
        
        Args:
            strategy: "time", "scene", or "adaptive"
            **kwargs: Additional parameters for VideoChunker
            
        Returns:
            Configured VideoChunker instance
        """
        return VideoChunker(**kwargs)
    
    @staticmethod
    def chunk_video(video_path: str, output_dir: str, 
                   strategy: str = "adaptive", **kwargs) -> List[Dict]:
        """
        Convenience method to chunk video with specified strategy.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save chunks
            strategy: "time", "scene", or "adaptive"
            **kwargs: Additional parameters
            
        Returns:
            List of chunk metadata
        """
        os.makedirs(output_dir, exist_ok=True)
        
        chunker = ChunkingStrategy.create_chunker(strategy, **kwargs)
        
        if strategy == "time":
            return chunker.chunk_video_by_time(video_path, output_dir)
        elif strategy == "scene":
            return chunker.chunk_video_by_scene(video_path, output_dir)
        else:  # adaptive
            return chunker.chunk_video_adaptive(video_path, output_dir)