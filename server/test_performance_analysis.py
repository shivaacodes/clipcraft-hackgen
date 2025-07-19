#!/usr/bin/env python3
"""
Test performance analysis for 60-second video processing
"""

import os
import sys
import asyncio
import requests
import time
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.performance_profiler import PerformanceProfiler

async def test_performance_analysis():
    """Test performance analysis for a 60-second video processing simulation."""
    
    print("📊 Performance Analysis for 60-Second Video Processing\n")
    
    # Test 1: Backend health check
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/api/v1/process/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
        return False
    
    # Test 2: Simulate performance analysis
    print("\n2. Simulating 60-second video processing...")
    
    # Create a mock profiler to simulate expected timings
    profiler = PerformanceProfiler("test_job_60s")
    
    # Simulate typical processing times for 60-second video
    operations = [
        ("video_download", 2.5, {"url": "cloudinary://test.mp4", "size": "15MB"}),
        ("chunking", 3.0, {"strategy": "time", "chunks": 2}),
        ("transcription", 45.0, {"model": "tiny", "chunks": 2}),  # Usually the slowest
        ("vibe_analysis", 8.0, {"vibe": "Happy", "chunks": 2}),
        ("clip_generation", 2.0, {"fast_mode": True, "clips": 2}),
    ]
    
    for op_name, duration, metadata in operations:
        start_time = time.time()
        
        # Simulate the operation
        print(f"   🔍 Running {op_name}...")
        await asyncio.sleep(0.1)  # Small delay to simulate processing
        
        # Create mock result
        from app.utils.performance_profiler import ProfilerResult
        result = ProfilerResult(
            name=op_name,
            start_time=start_time,
            end_time=start_time + duration,
            duration=duration,
            success=True,
            metadata=metadata
        )
        profiler.results.append(result)
        
        print(f"     ✅ {op_name}: {duration:.2f}s")
    
    # Analyze performance
    print("\n3. Performance Analysis Results:")
    profiler.print_summary()
    
    # Get bottleneck analysis
    print("\n4. Bottleneck Analysis:")
    bottlenecks = profiler.get_bottleneck_analysis()
    
    if bottlenecks["bottlenecks"]:
        print("   🐌 Bottlenecks found:")
        for bottleneck in bottlenecks["bottlenecks"]:
            severity = "🔴" if bottleneck["severity"] == "high" else "🟡"
            print(f"   {severity} {bottleneck['operation']}: {bottleneck['duration']:.2f}s ({bottleneck['percentage']:.1f}%)")
    else:
        print("   ✅ No major bottlenecks found")
    
    if bottlenecks["recommendations"]:
        print("\n5. Optimization Recommendations:")
        for rec in bottlenecks["recommendations"]:
            print(f"   💡 {rec['operation']}: {rec['suggestion']}")
            print(f"      Expected improvement: {rec['expected_improvement']}")
    
    # Test 3: Test actual performance endpoints
    print("\n6. Testing performance endpoints...")
    
    try:
        # Test recent performance endpoint
        response = requests.get("http://localhost:8000/api/v1/process/performance")
        if response.status_code == 200:
            data = response.json()
            recent_jobs = data.get("recent_jobs", [])
            print(f"   ✅ Recent performance data: {len(recent_jobs)} jobs")
            
            if recent_jobs:
                print("   📊 Recent job performance:")
                for job in recent_jobs[:3]:  # Show top 3
                    print(f"      - Job {job['job_id'][:8]}: {job['total_time']:.2f}s ({job['status']})")
                    print(f"        Slowest: {job['slowest_operation']}")
        else:
            print(f"   ❌ Performance endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Performance endpoint error: {e}")
    
    # Expected performance targets
    print("\n7. Performance Targets vs Reality:")
    target_times = {
        "video_download": 3.0,
        "chunking": 2.0,
        "transcription": 20.0,  # Target with tiny model
        "vibe_analysis": 5.0,
        "clip_generation": 1.0
    }
    
    total_target = sum(target_times.values())
    actual_total = profiler.get_total_duration()
    
    print(f"   🎯 Target total time: {total_target:.2f}s")
    print(f"   ⏱️ Simulated actual time: {actual_total:.2f}s")
    
    if actual_total > total_target:
        print(f"   ⚠️ Performance issue detected! {actual_total - total_target:.2f}s slower than target")
        
        # Identify which operations are over target
        print("   🔍 Operations over target:")
        for result in profiler.results:
            target = target_times.get(result.name, 0)
            if result.duration > target:
                print(f"      ⚠️ {result.name}: {result.duration:.2f}s vs {target:.2f}s target (+{result.duration - target:.2f}s)")
    else:
        print("   ✅ Performance within target!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_performance_analysis())
    
    if success:
        print("\n🎉 Performance Analysis Complete!")
        print("\n📋 Common 60-Second Video Issues:")
        print("   🐌 Transcription (Whisper): 20-60s (use tiny model)")
        print("   🐌 Vibe Analysis (Claude): 5-15s (optimize prompts)")
        print("   🐌 Download: 2-10s (depends on connection)")
        print("   ⚡ Clip Generation: 0.5-2s (fast mode)")
        print("   ⚡ Chunking: 1-3s (limit chunks)")
        print("\n💡 To debug your specific case:")
        print("   1. Check browser console for performance data")
        print("   2. Look at backend logs for timing info")
        print("   3. Use fast mode for development")
        print("   4. Check network speed for download")
        print("   5. Monitor CPU usage during transcription")
    else:
        print("\n💥 Performance analysis failed!")