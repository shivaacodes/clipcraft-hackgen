#!/usr/bin/env python3
"""
Test the complete video processing pipeline
"""

import requests
import time
import json

def test_complete_pipeline():
    """Test the complete pipeline with a real video."""
    import os
    
    base_url = "http://localhost:8000"
    
    # Test video file path (use direct file path for testing)
    test_video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    print("🎬 Testing complete video processing pipeline...")
    print(f"📹 Video file: {test_video_path}")
    
    if not os.path.exists(test_video_path):
        print(f"❌ Video file not found: {test_video_path}")
        return False
    
    # Step 1: Start processing using file upload
    print("🚀 Starting video processing...")
    
    # Prepare multipart form data
    with open(test_video_path, 'rb') as video_file:
        files = {'file': ('test_video.mp4', video_file, 'video/mp4')}
        
        data = {
            'chunk_strategy': 'adaptive',
            'include_vibe_analysis': 'true',
            'project_context': json.dumps({
                "name": "Test Project",
                "type": "Travel", 
                "genre": "Adventure",
                "language": "English",
                "selected_vibe": "Happy",
                "selected_age_group": "young-adults"
            })
        }
        
        response = requests.post(
            f"{base_url}/api/v1/process/upload-and-analyze",
            files=files,
            data=data
        )
    
    if response.status_code != 200:
        print(f"❌ Failed to start processing: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    job_id = result.get("job_id")
    print(f"✅ Processing started. Job ID: {job_id}")
    
    # Step 2: Poll for status
    print("⏳ Polling for results...")
    max_attempts = 30  # 1 minute max
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(2)
        attempt += 1
        
        status_response = requests.get(f"{base_url}/api/v1/process/status/{job_id}")
        if status_response.status_code != 200:
            print(f"❌ Failed to get status: {status_response.status_code}")
            continue
            
        status_data = status_response.json()
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        current_step = status_data.get("current_step", "unknown")
        
        print(f"📊 Status: {status} | Progress: {progress:.1f}% | Step: {current_step}")
        
        if status == "completed":
            print("🎉 Processing completed!")
            
            # Step 3: Get results
            result_response = requests.get(f"{base_url}/api/v1/process/result/{job_id}")
            if result_response.status_code == 200:
                result_data = result_response.json()
                
                print("\n📋 RESULTS:")
                print("=" * 50)
                
                # Transcription info
                transcription = result_data.get("transcription", {})
                merged = transcription.get("merged_transcription", {})
                stats = transcription.get("processing_stats", {})
                
                print(f"📝 Transcription:")
                print(f"   Total chunks: {stats.get('total_chunks', 0)}")
                print(f"   Successful: {stats.get('successful_chunks', 0)}")
                print(f"   Success rate: {stats.get('success_rate', 0):.1%}")
                print(f"   Text preview: {merged.get('text', '')[:100]}...")
                
                # Vibe analysis info
                vibe_analysis = result_data.get("vibe_analysis", {})
                if vibe_analysis:
                    vibe_result = vibe_analysis.get("vibe_analysis", {})
                    clips = vibe_result.get("top_clips", [])
                    
                    print(f"\n🎭 Vibe Analysis:")
                    print(f"   Selected vibe: {vibe_result.get('selected_vibe')}")
                    print(f"   Age group: {vibe_result.get('selected_age_group')}")
                    print(f"   Clips found: {len(clips)}")
                    
                    for i, clip in enumerate(clips[:3]):  # Show first 3
                        print(f"\n   Clip {i+1}: {clip.get('title', 'Untitled')}")
                        print(f"      Time: {clip.get('start_time', 0):.1f}s - {clip.get('end_time', 0):.1f}s")
                        print(f"      Overall score: {clip.get('scores', {}).get('overall', 0)}/100")
                        print(f"      Reason: {clip.get('reason', 'No reason')[:60]}...")
                
                return True
            else:
                print(f"❌ Failed to get results: {result_response.status_code}")
                return False
                
        elif status == "failed":
            error = status_data.get("error", "Unknown error")
            print(f"💥 Processing failed: {error}")
            return False
    
    print("⏰ Polling timed out")
    return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    if success:
        print("\n🎊 Pipeline test completed successfully!")
    else:
        print("\n💔 Pipeline test failed!")