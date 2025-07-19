#!/usr/bin/env python3
"""
Test fast clip generation with optimized settings
"""

import os
import sys
import asyncio
import time

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clip_generator import ClipGenerator

async def test_fast_clip_generation():
    """Test optimized clip generation speed."""
    
    video_path = "../public/uploads/videos/OkSHqqc0PteGbus5CaNVdB4iYEUtQ5gu_1751951306681.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print("⚡ Testing FAST clip generation...")
    
    # Create clip generator
    clip_generator = ClipGenerator()
    
    # Mock vibe analysis result with shorter clips for speed
    mock_vibe_analysis = {
        'vibe_analysis': {
            'selected_vibe': 'Happy',
            'selected_age_group': 'young-adults',
            'top_clips': [
                {
                    'title': 'Fast Clip 1',
                    'start_time': 5.0,
                    'end_time': 10.0,  # Only 5 seconds
                    'duration': 5.0,
                    'vibe': 'Happy',
                    'scores': {
                        'overall': 85,
                        'vibe_match': 90,
                        'age_group_match': 80,
                        'clip_potential': 85
                    },
                    'reason': 'Short test clip for speed testing'
                },
                {
                    'title': 'Fast Clip 2', 
                    'start_time': 15.0,
                    'end_time': 20.0,  # Only 5 seconds
                    'duration': 5.0,
                    'vibe': 'Happy',
                    'scores': {
                        'overall': 78,
                        'vibe_match': 85,
                        'age_group_match': 75,
                        'clip_potential': 75
                    },
                    'reason': 'Another short test clip'
                }
            ]
        }
    }
    
    try:
        start_time = time.time()
        
        # Generate clips with fast mode
        generated_clips = await clip_generator.generate_clips_from_analysis(
            video_path, mock_vibe_analysis, max_clips=2, fast_mode=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⚡ FAST MODE: Generated {len(generated_clips)} clips in {duration:.2f} seconds!")
        
        for i, clip in enumerate(generated_clips):
            print(f"\n📋 Clip {i+1}:")
            print(f"   📁 File: {clip['filename']}")
            print(f"   🖼️ Thumbnail: {clip.get('thumbnail_filename', 'None')}")
            print(f"   ⏱️ Duration: {clip['duration']:.1f}s")
            print(f"   📏 Size: {clip['file_size'] / 1024:.1f} KB")
            print(f"   🔗 URL: {clip['url']}")
            
            # Check if files exist
            if os.path.exists(clip['file_path']):
                print(f"   ✅ Video file exists")
            else:
                print(f"   ❌ Video file missing")
                
            if clip.get('thumbnail_path') and os.path.exists(clip['thumbnail_path']):
                print(f"   ✅ Thumbnail exists")
            else:
                print(f"   ❌ Thumbnail missing")
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        print(f"   ⚡ Total time: {duration:.2f} seconds")
        print(f"   🎬 Clips per second: {len(generated_clips) / duration:.2f}")
        print(f"   ⏱️ Average time per clip: {duration / len(generated_clips):.2f}s")
        
        if duration < 10:  # Less than 10 seconds is good
            print(f"   ✅ Performance: EXCELLENT!")
        elif duration < 20:
            print(f"   ⚠️ Performance: GOOD")
        else:
            print(f"   ❌ Performance: NEEDS IMPROVEMENT")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating clips: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fast_clip_generation())
    if success:
        print("\n🎉 Fast clip generation test successful!")
        print("⚡ Optimizations working properly!")
    else:
        print("\n💥 Fast clip generation test failed!")