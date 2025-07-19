"""
Whisper transcription service using whisper.cpp for local, fast transcription.
This service handles audio transcription and provides structured output.
"""

import os
import json
import subprocess
import tempfile
import asyncio
import time
from typing import List, Dict, Optional, Union
from pathlib import Path
import logging
# Add for audio checks
import soundfile as sf
import numpy as np
import requests
from sarvamai import SarvamAI

logger = logging.getLogger(__name__)

class WhisperCppService:
    """
    Service for transcribing audio using whisper.cpp.
    Assumes whisper.cpp is installed and available in PATH or specified location.
    """
    
    def __init__(self, 
                 whisper_executable: str = "whisper",  # or full path to whisper.cpp main
                 model_path: Optional[str] = None,  # path to ggml model file
                 language: str = "auto",
                 threads: int = 4):
        self.whisper_executable = whisper_executable
        self.model_path = model_path
        self.language = language
        self.threads = threads
        self._use_mock = False
        self._use_openai_whisper = False
        self._whisper_model = None
        
        # Verify whisper is available
        self._verify_whisper_installation()
    
    def _verify_whisper_installation(self):
        """Verify that whisper is properly installed and accessible."""
        try:
            # Try OpenAI Whisper Python package first
            import whisper
            logger.info("✅ Using OpenAI Whisper Python package")
            self._use_openai_whisper = True
            self._use_mock = False
            return
        except ImportError:
            pass
        
        try:
            # Try whisper.cpp executable
            result = subprocess.run([self.whisper_executable, "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError(f"whisper.cpp not working properly: {result.stderr}")
            logger.info("✅ Using whisper.cpp executable")
            self._use_openai_whisper = False
            self._use_mock = False
        except FileNotFoundError:
            logger.warning(f"Neither OpenAI Whisper package nor whisper.cpp found. Using mock transcription.")
            self._use_mock = True
            self._use_openai_whisper = False
        except subprocess.TimeoutExpired:
            logger.warning("whisper.cpp installation check timed out. Using mock transcription.")
            self._use_mock = True
            self._use_openai_whisper = False
    
    async def transcribe_audio(self, audio_path: str, output_format: str = "json", language: str = None) -> Dict:
        """
        Transcribe a single audio file using Sarvam AI SDK for Malayalam, Whisper for English/others.
        Args:
            audio_path: Path to audio file
            output_format: Output format ("json", "txt", "srt", "vtt")
            language: Language code ("en", "ml", etc.)
        Returns:
            Transcription result dictionary
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Use Sarvam AI SDK for Malayalam
        lang = language or self.language or "auto"
        if lang == "ml":
            logger.info(f"[SarvamAI] Using Sarvam AI SDK for Malayalam transcription: {audio_path}")
            sarvam_api_key = os.getenv("SARVAM_API_KEY", "")
            if not sarvam_api_key:
                logger.error("[SarvamAI] SARVAM_API_KEY not set in environment!")
                raise RuntimeError("SARVAM_API_KEY not set in environment!")
            try:
                client = SarvamAI(api_subscription_key=sarvam_api_key)
                with open(audio_path, "rb") as f:
                    response = client.speech_to_text.transcribe(
                        file=f,
                        model="saarika:v2.5",
                        language_code="ml-IN"
                    )
                text = getattr(response, "transcript", "") or getattr(response, "text", "")
                segments = getattr(response, "segments", [])
                return {
                    "text": text,
                    "segments": segments,
                    "confidence": 1.0,
                    "word_count": len(text.split()),
                    "duration": None,
                    "language": "ml",
                    "source_file": os.path.basename(audio_path),
                    "processing_info": {"provider": "sarvam.ai"}
                }
            except Exception as e:
                logger.error(f"[SarvamAI] Error transcribing with Sarvam AI SDK: {e}")
                raise

        # --- Audio sanity checks ---
        try:
            data, rate = sf.read(audio_path)
            # Always cast to float32 for Whisper compatibility
            data = data.astype(np.float32)
            if data.shape[0] == 0:
                logger.warning(f"[AudioCheck] Skipping empty audio chunk: {audio_path}")
                raise ValueError(f"Audio file {audio_path} is empty.")
            if np.all(data == 0):
                logger.warning(f"[AudioCheck] Audio chunk is silent (all zeros): {audio_path}")
                raise ValueError(f"Audio file {audio_path} is silent (all zeros).")
            if np.isnan(data).any():
                logger.error(f"[AudioCheck] {audio_path} contains NaNs! First 10: {data[:10]}")
                raise ValueError(f"Audio file {audio_path} contains NaNs.")
            if np.isinf(data).any():
                logger.error(f"[AudioCheck] {audio_path} contains Infs! First 10: {data[:10]}")
                raise ValueError(f"Audio file {audio_path} contains Infs.")
            duration = data.shape[0] / rate if data.ndim > 0 else 0
            min_duration = 0.5  # seconds
            if duration < min_duration:
                logger.warning(f"[AudioCheck] Skipping too-short chunk: {audio_path} (duration={duration:.2f}s)")
                logger.info(f"[AudioCheck] First 10 samples: {data[:10]}")
                raise ValueError(f"Audio file {audio_path} is too short for transcription.")
            if np.std(data) < 1e-5:
                logger.error(f"[AudioCheck] {audio_path} has near-zero variance! First 10: {data[:10]}")
                raise ValueError(f"Audio file {audio_path} has near-zero variance.")
            def is_silent(audio, threshold=1e-4, min_nonzero_ratio=0.01):
                # If less than 1% of samples are above threshold, treat as silent
                return (np.abs(audio) < threshold).sum() > (1 - min_nonzero_ratio) * audio.size
            if is_silent(data):
                logger.warning(f"[AudioCheck] Skipping silent chunk: {audio_path}")
                logger.info(f"[AudioCheck] First 10 samples: {data[:10]}")
                raise ValueError(f"Audio file {audio_path} is silent.")
            # Detailed diagnostics
            logger.info(f"[AudioCheck] {audio_path}: shape={data.shape}, rate={rate}, dtype={data.dtype}, duration={duration:.2f}s, mean={np.mean(data):.4f}, std={np.std(data):.4f}, max={np.max(data):.4f}, min={np.min(data):.4f}")
            # Optionally, log log_mel shape if OpenAI Whisper is available
            try:
                import whisper
                mel = whisper.log_mel_spectrogram(data)
                if hasattr(mel, 'numel') and mel.numel() == 0:
                    logger.warning(f"[AudioCheck] Skipping empty log_mel tensor for Whisper: {audio_path}")
                    raise ValueError(f"Empty log_mel tensor for {audio_path}, skipping chunk.")
                logger.info(f"[AudioCheck] log_mel shape: {mel.shape}")
            except Exception as mel_e:
                logger.info(f"[AudioCheck] Could not compute log_mel: {mel_e}")
        except Exception as e:
            logger.error(f"[AudioCheck] Could not read or check audio {audio_path}: {e}")
            raise
        # --- End audio sanity checks ---
        
        # Use mock transcription if neither whisper available
        if self._use_mock:
            return self._generate_mock_transcription(audio_path)
        
        # Use OpenAI Whisper Python package
        if self._use_openai_whisper:
            return await self._transcribe_with_openai_whisper(audio_path, language=lang)
        
        # Use whisper.cpp executable
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, f"output.{output_format}")
            
            # Build whisper.cpp command
            cmd = [
                self.whisper_executable,
                "-f", audio_path,  # input file
                "-oj",  # output json
                "-of", output_file,  # output file
                "-t", str(self.threads),  # number of threads
            ]
            
            # Add model if specified
            if self.model_path:
                cmd.extend(["-m", self.model_path])
                
            # Add language if not auto
            if self.language != "auto":
                cmd.extend(["-l", self.language])
                
            try:
                # Run whisper.cpp asynchronously
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise RuntimeError(f"Whisper transcription failed: {stderr.decode()}")
                
                # Read the JSON output
                json_output_file = output_file + ".json"
                if os.path.exists(json_output_file):
                    with open(json_output_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                else:
                    # Fallback: parse stdout if JSON file not created
                    result = self._parse_whisper_output(stdout.decode())
                
                return self._process_transcription_result(result, audio_path)
                
            except asyncio.TimeoutError:
                raise RuntimeError("Whisper transcription timed out")
            except Exception as e:
                logger.error(f"Error transcribing {audio_path}: {e}")
                raise
    
    async def transcribe_chunks(self, chunks: List[Dict], 
                              progress_callback=None) -> List[Dict]:
        """
        Transcribe multiple audio chunks concurrently.
        
        Args:
            chunks: List of chunk dictionaries from chunking service
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of transcription results with chunk metadata
        """
        results = []
        total_chunks = len(chunks)
        
        # Process chunks with controlled concurrency
        semaphore = asyncio.Semaphore(3)  # Limit concurrent transcriptions
        
        async def transcribe_chunk(chunk: Dict, index: int) -> Dict:
            async with semaphore:
                start_time = time.time()
                logger.info(f"[Transcription] Starting chunk {chunk.get('id', index)}: {chunk.get('path')}")
                try:
                    transcription = await self.transcribe_audio(chunk['path'])
                    end_time = time.time()
                    duration = end_time - start_time
                    logger.info(f"[Transcription] Finished chunk {chunk.get('id', index)}: {chunk.get('path')} in {duration:.2f} seconds")
                    result = {
                        **chunk,  # Include original chunk metadata
                        'transcription': transcription,
                        'success': True,
                        'error': None
                    }
                    if progress_callback:
                        await progress_callback(index + 1, total_chunks, result)
                    return result
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    logger.error(f"[Transcription] Failed chunk {chunk.get('id', index)}: {chunk.get('path')} after {duration:.2f} seconds. Error: {e}")
                    result = {
                        **chunk,
                        'transcription': None,
                        'success': False,
                        'error': str(e)
                    }
                    if progress_callback:
                        await progress_callback(index + 1, total_chunks, result)
                    return result
        
        # Create tasks for all chunks
        tasks = [transcribe_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        
        # Execute all transcriptions
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {i} failed with exception: {result}")
                valid_results.append({
                    **chunks[i],
                    'transcription': None,
                    'success': False,
                    'error': str(result)
                })
            else:
                valid_results.append(result)
        
        return valid_results
    
    def _parse_whisper_output(self, output: str) -> Dict:
        """Parse whisper.cpp output when JSON file is not available."""
        # This is a fallback parser for plain text output
        lines = output.strip().split('\n')
        segments = []
        
        current_segment = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to parse timestamp format: [00:00:00.000 --> 00:00:05.000]
            if line.startswith('[') and '-->' in line:
                if current_segment:
                    segments.append(current_segment)
                
                times = line.strip('[]').split(' --> ')
                current_segment = {
                    'start': self._parse_timestamp(times[0]),
                    'end': self._parse_timestamp(times[1]) if len(times) > 1 else 0,
                    'text': ''
                }
            else:
                # This is transcribed text
                if current_segment:
                    current_segment['text'] += (' ' + line).strip()
        
        if current_segment:
            segments.append(current_segment)
        
        return {
            'segments': segments,
            'text': ' '.join(seg.get('text', '') for seg in segments)
        }
    
    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert timestamp string (HH:MM:SS.mmm) to seconds."""
        try:
            parts = timestamp.split(':')
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            return 0.0
        except (ValueError, IndexError):
            return 0.0
    
    def _process_transcription_result(self, raw_result: Dict, audio_path: str) -> Dict:
        """Process and enhance transcription result."""
        text = raw_result.get('text', '').strip()
        segments = raw_result.get('segments', [])
        
        # Calculate confidence score (if available)
        confidence = self._calculate_confidence(segments)
        
        # Extract key metrics
        word_count = len(text.split()) if text else 0
        duration = segments[-1].get('end', 0) if segments else 0
        
        return {
            'text': text,
            'segments': segments,
            'confidence': confidence,
            'word_count': word_count,
            'duration': duration,
            'language': raw_result.get('language', 'unknown'),
            'source_file': os.path.basename(audio_path),
            'processing_info': {
                'model': self.model_path or 'default',
                'threads': self.threads,
                'segments_count': len(segments)
            }
        }
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """Calculate average confidence score from segments."""
        if not segments:
            return 0.0
        
        confidences = []
        for segment in segments:
            # whisper.cpp doesn't always provide confidence, estimate from text quality
            text = segment.get('text', '')
            if text:
                # Simple heuristic: longer segments with proper punctuation = higher confidence
                base_confidence = min(0.9, len(text) / 100)  # Max 0.9 based on length
                if any(punct in text for punct in '.!?'):
                    base_confidence += 0.05
                if text[0].isupper():  # Proper capitalization
                    base_confidence += 0.05
                confidences.append(min(1.0, base_confidence))
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        return [
            'wav', 'mp3', 'm4a', 'ogg', 'flac', 
            'aac', 'wma', 'opus', 'webm'
        ]
    
    def get_model_info(self) -> Dict:
        """Get information about the current whisper model."""
        return {
            'executable': self.whisper_executable,
            'model_path': self.model_path,
            'language': self.language,
            'threads': self.threads,
            'supported_formats': self.get_supported_formats(),
            'using_mock': self._use_mock,
            'using_openai_whisper': self._use_openai_whisper
        }
    
    async def _transcribe_with_openai_whisper(self, audio_path: str, language: str = None) -> Dict:
        """Transcribe audio using OpenAI Whisper Python package."""
        try:
            import whisper
            
            # Load model if not already loaded (use base model for better accuracy)
            if self._whisper_model is None:
                model_name = "base"  # Use base model for better accuracy
                logger.info(f"🔄 Loading Whisper model: {model_name}")
                self._whisper_model = whisper.load_model(model_name)
                logger.info(f"✅ Whisper model loaded")
            
            # Transcribe audio
            logger.info(f"🎙️ Transcribing audio file: {audio_path}")
            
            # Run in thread pool to avoid blocking
            def transcribe_sync():
                return self._whisper_model.transcribe(
                    audio_path,
                    language=None if (language or self.language) == "auto" else (language or self.language),
                    fp16=False,  # Use fp32 for compatibility
                    verbose=False,
                    # Speed optimizations
                    word_timestamps=False,  # Disable word-level timestamps for speed
                    condition_on_previous_text=False  # Disable for speed
                )
            
            # Run transcription in thread pool
            result = await asyncio.to_thread(transcribe_sync)
            
            logger.info(f"✅ Transcription completed for {audio_path}")
            # Print transcription text to terminal (console.log equivalent)
            print(f"[TranscriptionResult] {audio_path}: {result.get('text', '')}")
            
            return self._process_transcription_result(result, audio_path)
            
        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed: {e}")
            raise
    
    def _generate_mock_transcription(self, audio_path: str) -> Dict:
        """Generate mock transcription data for testing."""
        import random
        
        # Get file duration estimation from file size
        file_size = os.path.getsize(audio_path)
        estimated_duration = min(30.0, max(5.0, file_size / 50000))  # Rough estimate
        
        # Sample transcription texts for different vibes
        sample_texts = [
            "This is an amazing journey through beautiful landscapes with stunning views and incredible adventures.",
            "The dramatic tension builds as our characters face unexpected challenges and emotional revelations.",
            "High energy action packed sequences with intense moments that keep you on the edge of your seat.",
            "Fun and entertaining content with lots of laughter, jokes, and lighthearted moments throughout.",
            "Inspiring stories of perseverance, growth, and achievement that motivate and uplift the audience.",
            "Mysterious elements unfold as secrets are revealed and unexpected plot twists emerge gradually.",
            "Emotional depth and heartfelt moments that connect with viewers on a personal and meaningful level.",
            "Cool and stylish presentation with modern aesthetics and contemporary appeal for today's audience.",
            "Musical elements and rhythmic content that creates an engaging audio-visual experience for listeners."
        ]
        
        # Generate segments
        num_segments = max(1, int(estimated_duration / 5))  # ~5 seconds per segment
        segments = []
        full_text_parts = []
        
        for i in range(num_segments):
            start_time = i * (estimated_duration / num_segments)
            end_time = min(estimated_duration, (i + 1) * (estimated_duration / num_segments))
            
            # Choose random text snippet
            text = random.choice(sample_texts)
            words = text.split()
            # Take a portion of the text for this segment
            segment_words = words[:random.randint(5, 15)]
            segment_text = " ".join(segment_words)
            
            segments.append({
                'start': start_time,
                'end': end_time,
                'text': segment_text
            })
            full_text_parts.append(segment_text)
        
        full_text = " ".join(full_text_parts)
        
        # Process and return in the expected format
        result = {
            'text': full_text,
            'segments': segments,
            'language': 'en'
        }
        
        return self._process_transcription_result(result, audio_path)


class TranscriptionManager:
    """
    High-level manager for video transcription workflow.
    Combines chunking and transcription services.
    """
    
    def __init__(self, whisper_service: WhisperCppService):
        self.whisper_service = whisper_service
    
    async def transcribe_video_file(self, video_path: str, 
                                  chunk_strategy: str = "adaptive",
                                  progress_callback=None) -> Dict:
        """
        Complete workflow: chunk video and transcribe all chunks.
        
        Args:
            video_path: Path to video file
            chunk_strategy: Chunking strategy ("time", "scene", "adaptive")
            progress_callback: Progress callback function
            
        Returns:
            Complete transcription result with chunks and merged text
        """
        from ..utils.chunking import ChunkingStrategy
        
        # Create temporary directory for chunks
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Chunk the video
            chunks = ChunkingStrategy.chunk_video(
                video_path, temp_dir, strategy=chunk_strategy
            )
            
            if not chunks:
                raise ValueError("No valid chunks created from video")
            
            # Step 2: Transcribe all chunks
            transcription_results = await self.whisper_service.transcribe_chunks(
                chunks, progress_callback
            )
            
            # Step 3: Merge results
            merged_result = self._merge_transcriptions(transcription_results)
            
            return {
                'video_path': video_path,
                'chunk_strategy': chunk_strategy,
                'chunks': transcription_results,
                'merged_transcription': merged_result,
                'processing_stats': self._calculate_stats(transcription_results)
            }
    
    def _merge_transcriptions(self, chunk_results: List[Dict]) -> Dict:
        """Merge transcriptions from multiple chunks into coherent text."""
        successful_chunks = [r for r in chunk_results if r.get('success')]
        
        if not successful_chunks:
            return {'text': '', 'segments': [], 'confidence': 0.0}
        
        # Sort chunks by start time
        successful_chunks.sort(key=lambda x: x.get('start_time', 0))
        
        merged_text = []
        merged_segments = []
        confidences = []
        
        for chunk in successful_chunks:
            transcription = chunk.get('transcription', {})
            text = transcription.get('text', '').strip()
            
            if text:
                merged_text.append(text)
                
                # Adjust segment timestamps to absolute video time
                chunk_start = chunk.get('start_time', 0)
                segments = transcription.get('segments', [])
                
                for segment in segments:
                    adjusted_segment = {
                        **segment,
                        'start': segment.get('start', 0) + chunk_start,
                        'end': segment.get('end', 0) + chunk_start,
                        'chunk_id': chunk.get('id')
                    }
                    merged_segments.append(adjusted_segment)
                
                confidence = transcription.get('confidence', 0)
                if confidence > 0:
                    confidences.append(confidence)
        
        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'text': ' '.join(merged_text),
            'segments': merged_segments,
            'confidence': overall_confidence,
            'chunk_count': len(successful_chunks)
        }
    
    def _calculate_stats(self, chunk_results: List[Dict]) -> Dict:
        """Calculate processing statistics."""
        total_chunks = len(chunk_results)
        successful_chunks = sum(1 for r in chunk_results if r.get('success'))
        failed_chunks = total_chunks - successful_chunks
        
        total_duration = sum(r.get('duration', 0) for r in chunk_results)
        
        word_counts = []
        for result in chunk_results:
            if result.get('success') and result.get('transcription'):
                word_count = result['transcription'].get('word_count', 0)
                if word_count > 0:
                    word_counts.append(word_count)
        
        return {
            'total_chunks': total_chunks,
            'successful_chunks': successful_chunks,
            'failed_chunks': failed_chunks,
            'success_rate': successful_chunks / total_chunks if total_chunks > 0 else 0,
            'total_duration': total_duration,
            'total_words': sum(word_counts),
            'average_words_per_chunk': sum(word_counts) / len(word_counts) if word_counts else 0
        }