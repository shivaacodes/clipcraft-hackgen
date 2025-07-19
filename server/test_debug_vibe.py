#!/usr/bin/env python3
"""
Debug vibe analysis to see why no clips were generated
"""

import os
import sys
import asyncio
import requests
import time
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_vibe_analysis():
    """Debug the vibe analysis step."""
    
    print("🔍 Debugging vibe analysis...")
    
    # Test with simple text analysis
    print("📝 Testing text-only vibe analysis...")
    try:
        test_text = "This is a happy and energetic video with lots of fun moments. The speaker is excited and talking about amazing things that happened. There's laughter and positive energy throughout."
        
        params = {
            "text": test_text
        }
        
        project_context = {
            "selected_vibe": "Happy",
            "selected_age_group": "young-adults"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/process/analyze-text",
            params=params,
            json=project_context,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text analysis successful!")
            print(f"📊 Analysis result: {json.dumps(result, indent=2)}")
            
            vibe_analysis = result.get('vibe_analysis', {})
            top_clips = vibe_analysis.get('top_clips', [])
            print(f"🎬 Found {len(top_clips)} clips in text analysis")
            
            return True
        else:
            print(f"❌ Text analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Text analysis error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_vibe_analysis())
    if success:
        print("\n✅ Vibe analysis debug successful!")
    else:
        print("\n❌ Vibe analysis debug failed!")