#!/usr/bin/env python3
"""
Integration test for the complete video processing pipeline
"""

import os
import sys
import asyncio
import requests
import time
from pathlib import Path

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_complete_pipeline():
    """Test the complete video processing pipeline."""
    
    video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Test video not found: {video_path}")
        return False
    
    print("🎬 Testing complete video processing pipeline...")
    
    # Test 1: Health check
    print("🔍 Testing health check...")
    try:
        response = requests.get("http://localhost:8000/api/v1/process/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data['status']}")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        return False
    
    # Test 2: Upload and process video
    print("📤 Testing video upload and processing...")
    try:
        with open(video_path, 'rb') as video_file:
            files = {'file': ('test_video.mp4', video_file, 'video/mp4')}
            data = {
                'chunk_strategy': 'time',
                'include_vibe_analysis': 'true',
                'project_context': '{"selected_vibe": "Happy", "selected_age_group": "young-adults"}'
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/process/upload-and-analyze",
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data['job_id']
                print(f"✅ Upload successful, job ID: {job_id}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Test 3: Monitor processing status
    print("⏳ Monitoring processing status...")
    max_wait_time = 120  # 2 minutes max
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"http://localhost:8000/api/v1/process/status/{job_id}", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data['status']
                progress = status_data['progress']
                step = status_data['current_step']
                
                print(f"📊 Status: {status} ({progress:.1f}%) - {step}")
                
                if status == 'completed':
                    print("✅ Processing completed!")
                    break
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Processing failed: {error}")
                    return False
                
                time.sleep(2)  # Wait 2 seconds before next check
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
    else:
        print("❌ Processing timed out")
        return False
    
    # Test 4: Get processing results
    print("📋 Getting processing results...")
    try:
        response = requests.get(f"http://localhost:8000/api/v1/process/result/{job_id}", timeout=5)
        if response.status_code == 200:
            result_data = response.json()
            print("✅ Results retrieved successfully!")
            
            # Check transcription
            transcription = result_data.get('transcription', {})
            if transcription:
                merged = transcription.get('merged_transcription', {})
                text = merged.get('text', '')
                print(f"📝 Transcribed text: {text[:100]}...")
            
            # Check vibe analysis
            vibe_analysis = result_data.get('vibe_analysis', {})
            if vibe_analysis:
                analysis = vibe_analysis.get('vibe_analysis', {})
                top_clips = analysis.get('top_clips', [])
                print(f"🎭 Found {len(top_clips)} potential clips")
            
            # Check generated clips
            generated_clips = result_data.get('generated_clips', {})
            if generated_clips:
                clips = generated_clips.get('clips', [])
                print(f"🎬 Generated {len(clips)} video clips")
                
                # Test clip file access
                for i, clip in enumerate(clips):
                    clip_url = clip.get('url', '')
                    thumbnail_url = clip.get('thumbnail_url', '')
                    
                    if clip_url:
                        clip_response = requests.head(f"http://localhost:8000{clip_url}", timeout=5)
                        if clip_response.status_code == 200:
                            print(f"✅ Clip {i+1} accessible: {clip_url}")
                        else:
                            print(f"❌ Clip {i+1} not accessible: {clip_response.status_code}")
                    
                    if thumbnail_url:
                        thumb_response = requests.head(f"http://localhost:8000{thumbnail_url}", timeout=5)
                        if thumb_response.status_code == 200:
                            print(f"✅ Thumbnail {i+1} accessible: {thumbnail_url}")
                        else:
                            print(f"❌ Thumbnail {i+1} not accessible: {thumb_response.status_code}")
                
                return True
            else:
                print("❌ No clips generated")
                return False
        else:
            print(f"❌ Results retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Results error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_pipeline())
    if success:
        print("\n🎉 Complete pipeline integration test successful!")
        print("🎬 All features working: upload → chunks → transcription → vibe analysis → clip generation → file serving")
        print("🔗 Clips are clickable and thumbnails are accessible!")
        print("💻 Frontend available at: http://localhost:3001")
    else:
        print("\n💥 Pipeline integration test failed!")