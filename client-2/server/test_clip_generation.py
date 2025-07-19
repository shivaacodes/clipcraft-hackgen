#!/usr/bin/env python3
"""
Test clip generation with thumbnails
"""

import os
import sys
import asyncio

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clip_generator import ClipGenerator

async def test_clip_generation():
    """Test clip generation with a real video."""
    
    video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print(f"🎬 Testing clip generation with: {video_path}")
    
    # Create clip generator
    clip_generator = ClipGenerator()
    
    # Mock vibe analysis result with some clips
    mock_vibe_analysis = {
        'vibe_analysis': {
            'selected_vibe': 'Happy',
            'selected_age_group': 'young-adults',
            'top_clips': [
                {
                    'title': 'Happy Clip 1',
                    'start_time': 5.0,
                    'end_time': 15.0,
                    'duration': 10.0,
                    'vibe': 'Happy',
                    'scores': {
                        'overall': 85,
                        'vibe_match': 90,
                        'age_group_match': 80,
                        'clip_potential': 85
                    },
                    'reason': 'This segment has positive energy and engaging content'
                },
                {
                    'title': 'Happy Clip 2', 
                    'start_time': 25.0,
                    'end_time': 35.0,
                    'duration': 10.0,
                    'vibe': 'Happy',
                    'scores': {
                        'overall': 78,
                        'vibe_match': 85,
                        'age_group_match': 75,
                        'clip_potential': 75
                    },
                    'reason': 'Good momentum and interesting visuals'
                }
            ]
        }
    }
    
    try:
        # Generate clips
        generated_clips = await clip_generator.generate_clips_from_analysis(
            video_path, mock_vibe_analysis, max_clips=2
        )
        
        print(f"✅ Generated {len(generated_clips)} clips!")
        
        for i, clip in enumerate(generated_clips):
            print(f"\n📋 Clip {i+1}:")
            print(f"   📁 File: {clip['filename']}")
            print(f"   🖼️ Thumbnail: {clip.get('thumbnail_filename', 'None')}")
            print(f"   ⏱️ Duration: {clip['duration']:.1f}s")
            print(f"   📏 Size: {clip['file_size'] / 1024:.1f} KB")
            print(f"   🔗 URL: {clip['url']}")
            print(f"   🎨 Thumbnail URL: {clip.get('thumbnail_url', 'None')}")
            
            # Check if files exist
            if os.path.exists(clip['file_path']):
                print(f"   ✅ Video file exists")
            else:
                print(f"   ❌ Video file missing")
                
            if clip.get('thumbnail_path') and os.path.exists(clip['thumbnail_path']):
                print(f"   ✅ Thumbnail exists")
            else:
                print(f"   ❌ Thumbnail missing")
        
        # Show generated files directory
        clips_dir = clip_generator.output_base_dir
        print(f"\n📂 Generated files in: {clips_dir}")
        if os.path.exists(clips_dir):
            files = os.listdir(clips_dir)
            for file in files:
                size = os.path.getsize(os.path.join(clips_dir, file))
                print(f"   📄 {file} ({size / 1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating clips: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_clip_generation())
    if success:
        print("\n🎉 Clip generation test successful!")
        print("🎬 You can now test the frontend at http://localhost:3000")
    else:
        print("\n💥 Clip generation test failed!")