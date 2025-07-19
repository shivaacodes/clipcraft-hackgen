#!/usr/bin/env python3
"""
Simple test for OpenAI Whisper transcription
"""

import tempfile
import asyncio
import os
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.whisper_service import WhisperCppService

async def test_whisper():
    """Test whisper transcription with a simple audio file."""
    
    # Create a simple test using one of the chunked audio files
    video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    # Create chunks first
    from app.utils.chunking import ChunkingStrategy
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print("📋 Creating audio chunks...")
        chunks = ChunkingStrategy.chunk_video(video_path, temp_dir, strategy="time")
        
        if not chunks:
            print("❌ No chunks created")
            return False
        
        print(f"✅ Created {len(chunks)} chunks")
        
        # Test whisper on first chunk
        first_chunk = chunks[0]
        print(f"🎙️ Testing transcription on: {first_chunk['filename']}")
        
        # Initialize whisper service
        whisper_service = WhisperCppService()
        
        try:
            result = await whisper_service.transcribe_audio(first_chunk['path'])
            
            print(f"✅ Transcription successful!")
            print(f"   Text: {result.get('text', '')[:100]}...")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Word count: {result.get('word_count', 0)}")
            print(f"   Duration: {result.get('duration', 0):.1f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_whisper())
    if success:
        print("🎉 Whisper test successful!")
    else:
        print("💥 Whisper test failed!")