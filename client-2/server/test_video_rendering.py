#!/usr/bin/env python3
"""
Test video rendering functionality directly
"""

import os
import sys
import asyncio
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.video_renderer import VideoRenderer, VideoRenderingManager

# Always use paths relative to this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

async def test_video_rendering():
    """Test video rendering with existing clips."""
    
    print("🎬 Testing Video Rendering Functionality\n")
    
    # Check for existing clips
    clips_dir = os.path.join(TEST_DIR, "generated_clips")
    
    if not os.path.exists(clips_dir):
        print("❌ No generated_clips directory found")
        return False
    
    # Find available clips
    clips = []
    for file in os.listdir(clips_dir):
        if file.startswith("clip_") and file.endswith(".mp4"):
            clips.append(file)
    
    if not clips:
        print("❌ No video clips found to render")
        return False
    
    print(f"📁 Found {len(clips)} clips to work with:")
    for clip in clips:
        print(f"   - {clip}")
    
    # Create mock timeline clips (limit to 2 for faster testing)
    timeline_clips = []
    for i, clip_file in enumerate(clips[:2]):
        # Extract info from filename
        parts = clip_file.replace(".mp4", "").split("_")
        if len(parts) >= 4:
            clip_num = parts[1]
            clip_id = parts[2]
            time_range = parts[3]
            
            timeline_clips.append({
                "timelineId": i + 1,
                "id": i + 1,
                "name": f"Test Clip {i + 1}",
                "duration": "0:10",
                "clip_url": f"/api/v1/process/clips/{clip_file}",
                "thumbnail_url": f"/api/v1/process/clips/thumb_{clip_num}_{clip_id}_{time_range.split('-')[0]}.jpg",
                "startTime": "0:05",
                "endTime": "0:15",
                "confidence": 0.85,
                "vibe": "Happy",
                "reason": "Test clip for rendering",
                "scores": {"overall": 85}
            })
    
    print(f"\n🎞️ Creating timeline with {len(timeline_clips)} clips:")
    for clip in timeline_clips:
        print(f"   - {clip['name']}: {clip['clip_url']}")
    
    # Test video rendering
    try:
        # Initialize renderer
        print("\n🔧 Initializing video renderer...")
        video_renderer = VideoRenderer()
        render_manager = VideoRenderingManager(video_renderer)
        
        # Prepare timeline data
        timeline_data = {
            'timeline_clips': timeline_clips
        }
        
        print("🎬 Starting video rendering...")
        render_result = await render_manager.render_project_video(
            timeline_data, 
            project_name="test_final_video"
        )
        
        print("✅ Video rendering completed!")
        print(f"📋 Render Result:")
        print(f"   File: {render_result['filename']}")
        print(f"   Path: {render_result['file_path']}")
        print(f"   Size: {render_result['file_size'] / 1024:.1f} KB")
        print(f"   Duration: {render_result['duration']:.1f}s")
        print(f"   Clips: {render_result['clips_count']}")
        print(f"   URL: {render_result['url']}")
        
        # Verify file exists
        if os.path.exists(render_result['file_path']):
            print("✅ Rendered video file exists")
            
            # Show rendered videos directory
            rendered_dir = os.path.join(TEST_DIR, "rendered_videos")
            print(f"\n📂 Rendered videos directory: {rendered_dir}")
            if os.path.exists(rendered_dir):
                files = os.listdir(rendered_dir)
                for file in files:
                    size = os.path.getsize(os.path.join(rendered_dir, file))
                    print(f"   📄 {file} ({size / 1024:.1f} KB)")
            
            return True
        else:
            print("❌ Rendered video file not found")
            return False
            
    except Exception as e:
        print(f"❌ Video rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_video_rendering_with_image():
    """Test video rendering with a video clip and an uploaded image."""
    print("\n🎬 Testing Video Rendering with Image in Timeline\n")
    # Check for existing clips
    clips_dir = os.path.join(TEST_DIR, "generated_clips")
    images_dir = os.path.join(TEST_DIR, "../public/assets/images")
    if not os.path.exists(clips_dir):
        print("❌ No generated_clips directory found")
        return False
    if not os.path.exists(images_dir):
        print("❌ No images directory found at titan/public/assets/images")
        return False
    # Find a video clip
    clips = [f for f in os.listdir(clips_dir) if f.startswith("clip_") and f.endswith(".mp4")]
    if not clips:
        print("❌ No video clips found to render")
        return False
    # Find an image
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg','.jpeg','.png'))]
    if not images:
        print("❌ No images found in titan/public/assets/images")
        return False
    image_file = images[0]
    print(f"🖼️ Using image: {image_file}")
    # Create timeline: 1 clip + 1 image
    timeline_clips = []
    # Add video clip
    clip_file = clips[0]
    parts = clip_file.replace(".mp4", "").split("_")
    if len(parts) >= 4:
        clip_num = parts[1]
        clip_id = parts[2]
        time_range = parts[3]
        timeline_clips.append({
            "timelineId": 1,
            "id": 1,
            "name": f"Test Clip",
            "duration": "3",
            "clip_url": f"/api/v1/process/clips/{clip_file}",
            "thumbnail_url": f"/api/v1/process/clips/thumb_{clip_num}_{clip_id}_{time_range.split('-')[0]}.jpg",
            "startTime": "0:00",
            "endTime": "0:03",
            "confidence": 0.85,
            "vibe": "Happy",
            "reason": "Test clip for rendering",
            "scores": {"overall": 85}
        })
    # Add image
    timeline_clips.append({
        "timelineId": 2,
        "id": 2,
        "name": image_file,
        "type": "image",
        "url": f"/assets/images/{image_file}",
        "duration": 3
    })
    print(f"\n🎞️ Creating timeline with {len(timeline_clips)} items (clip + image)")
    for item in timeline_clips:
        print(f"   - {item['name']} ({item.get('type','clip')})")
    # Test video rendering
    try:
        print("\n🔧 Initializing video renderer...")
        video_renderer = VideoRenderer()
        render_manager = VideoRenderingManager(video_renderer)
        timeline_data = {'timeline_clips': timeline_clips}
        print("🎬 Starting video rendering with image...")
        render_result = await render_manager.render_project_video(
            timeline_data,
            project_name="test_with_image"
        )
        print("✅ Video rendering with image completed!")
        print(f"   File: {render_result['filename']}")
        print(f"   Path: {render_result['file_path']}")
        print(f"   Size: {render_result['file_size'] / 1024:.1f} KB")
        print(f"   Duration: {render_result['duration']:.1f}s")
        print(f"   Clips: {render_result['clips_count']}")
        print(f"   URL: {render_result['url']}")
        if os.path.exists(render_result['file_path']):
            print("✅ Rendered video file exists (with image)")
            return True
        else:
            print("❌ Rendered video file not found")
            return False
    except Exception as e:
        print(f"❌ Video rendering with image failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n--- Running standard video rendering test ---")
    success = asyncio.run(test_video_rendering())
    if success:
        print("\n🎉 Video rendering test successful!")
        print("🔥 Final video stitching functionality is working!")
        print("📱 You can now test the frontend 'Render Final Video' button")
    else:
        print("\n💥 Video rendering test failed!")
    print("\n--- Running video rendering test with image ---")
    success_img = asyncio.run(test_video_rendering_with_image())
    if success_img:
        print("\n🎉 Video rendering with image test successful!")
        print("🖼️ Image stitching functionality is working!")
    else:
        print("\n💥 Video rendering with image test failed!")