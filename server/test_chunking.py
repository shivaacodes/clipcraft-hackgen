#!/usr/bin/env python3
"""
Test script for video chunking functionality
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.chunking import ChunkingStrategy

async def test_chunking():
    """Test video chunking with a sample video."""
    
    # Use one of the test videos
    video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Test video not found: {video_path}")
        return False
    
    print(f"🎬 Testing chunking with video: {video_path}")
    
    # Create temporary directory for chunks
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Test adaptive chunking
            print("📋 Testing adaptive chunking strategy...")
            chunks = ChunkingStrategy.chunk_video(
                video_path, 
                temp_dir, 
                strategy="adaptive"
            )
            
            print(f"✅ Successfully created {len(chunks)} chunks")
            
            # Print details about chunks
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"  Chunk {i+1}: {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s ({chunk['duration']:.1f}s)")
                print(f"    File: {chunk['filename']}")
                print(f"    Exists: {os.path.exists(chunk['path'])}")
                
                # Check file size
                if os.path.exists(chunk['path']):
                    size = os.path.getsize(chunk['path'])
                    print(f"    Size: {size / 1024:.1f} KB")
            
            if len(chunks) > 3:
                print(f"  ... and {len(chunks) - 3} more chunks")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during chunking: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_chunking())
    if success:
        print("🎉 Chunking test completed successfully!")
    else:
        print("💥 Chunking test failed!")
        sys.exit(1)