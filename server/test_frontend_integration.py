#!/usr/bin/env python3
"""
Test frontend integration by creating a mock response with actual generated clips
"""

import os
import json

def create_mock_response():
    """Create a mock API response with real generated clips for frontend testing."""
    
    clips_dir = "/Users/shivasajay/Desktop/Projects/OG-template/titan/server/generated_clips"
    
    # Find actual generated clips
    clips = []
    thumbnails = []
    
    for file in os.listdir(clips_dir):
        if file.startswith("clip_") and file.endswith(".mp4"):
            clips.append(file)
        elif file.startswith("thumb_") and file.endswith(".jpg"):
            thumbnails.append(file)
    
    print(f"Found {len(clips)} clips and {len(thumbnails)} thumbnails")
    
    # Create mock response structure
    mock_response = {
        "transcription": {
            "merged_transcription": {
                "text": "This is a test video with happy and engaging content. There are several interesting moments that could make great clips.",
                "confidence": 0.85
            }
        },
        "vibe_analysis": {
            "vibe_analysis": {
                "selected_vibe": "Happy",
                "selected_age_group": "young-adults",
                "clips_found": len(clips),
                "top_clips": []
            }
        },
        "generated_clips": {
            "total_generated": len(clips),
            "clips": [],
            "status": "success"
        }
    }
    
    # Add clips to response
    for i, clip_file in enumerate(clips[:3]):  # Limit to 3 clips
        # Extract info from filename
        # Format: clip_1_889f179c_5s-15s.mp4
        parts = clip_file.replace(".mp4", "").split("_")
        if len(parts) >= 4:
            clip_num = parts[1]
            clip_id = parts[2]
            time_range = parts[3]
            
            # Find matching thumbnail
            thumb_file = f"thumb_{clip_num}_{clip_id}_{time_range.split('-')[0]}.jpg"
            
            if thumb_file in thumbnails:
                clip_data = {
                    "title": f"Happy Clip {i+1}",
                    "start_time": 5.0 + (i * 20),
                    "end_time": 15.0 + (i * 20),
                    "duration": 10.0,
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
                    "thumbnail_url": f"/api/v1/process/clips/{thumb_file}",
                    "clip_filename": clip_file,
                    "thumbnail_filename": thumb_file,
                    "file_size": os.path.getsize(os.path.join(clips_dir, clip_file))
                }
                
                mock_response["vibe_analysis"]["vibe_analysis"]["top_clips"].append(clip_data)
                mock_response["generated_clips"]["clips"].append(clip_data)
    
    return mock_response

if __name__ == "__main__":
    response = create_mock_response()
    
    print("\n📊 Mock API Response Structure:")
    print(f"Clips found: {len(response['vibe_analysis']['vibe_analysis']['top_clips'])}")
    
    for i, clip in enumerate(response['vibe_analysis']['vibe_analysis']['top_clips']):
        print(f"\n🎬 Clip {i+1}:")
        print(f"   Title: {clip['title']}")
        print(f"   Video URL: {clip['clip_url']}")
        print(f"   Thumbnail URL: {clip['thumbnail_url']}")
        print(f"   Duration: {clip['duration']}s")
        print(f"   Scores: {clip['scores']}")
    
    # Save to file for testing
    with open("mock_response.json", "w") as f:
        json.dump(response, f, indent=2)
    
    print(f"\n✅ Mock response saved to mock_response.json")
    print("🔗 Test these URLs in browser:")
    for clip in response['vibe_analysis']['vibe_analysis']['top_clips']:
        print(f"   Video: http://localhost:8000{clip['clip_url']}")
        print(f"   Thumbnail: http://localhost:8000{clip['thumbnail_url']}")