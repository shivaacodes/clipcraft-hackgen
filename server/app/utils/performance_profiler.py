"""
Performance profiler for tracking processing pipeline timing
"""

import time
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ProfilerResult:
    """Result of a profiled operation"""
    name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class PerformanceProfiler:
    """
    Tracks timing and performance metrics for video processing pipeline
    """
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.results: List[ProfilerResult] = []
        self.start_time = time.time()
        self.current_operation = None
        
    def get_total_duration(self) -> float:
        """Get total duration since profiler started"""
        return time.time() - self.start_time
    
    @contextmanager
    def profile(self, operation_name: str, metadata: Dict = None):
        """Context manager for profiling operations"""
        start_time = time.time()
        self.current_operation = operation_name
        metadata = metadata or {}
        
        logger.info(f"🔍 [{self.job_id}] Starting: {operation_name}")
        
        try:
            yield
            
            # Success
            end_time = time.time()
            duration = end_time - start_time
            
            result = ProfilerResult(
                name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                metadata=metadata
            )
            
            self.results.append(result)
            logger.info(f"✅ [{self.job_id}] Completed: {operation_name} in {duration:.2f}s")
            
        except Exception as e:
            # Error
            end_time = time.time()
            duration = end_time - start_time
            
            result = ProfilerResult(
                name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=False,
                error=str(e),
                metadata=metadata
            )
            
            self.results.append(result)
            logger.error(f"❌ [{self.job_id}] Failed: {operation_name} in {duration:.2f}s - {e}")
            raise
        finally:
            self.current_operation = None
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        total_duration = self.get_total_duration()
        
        summary = {
            'job_id': self.job_id,
            'total_duration': total_duration,
            'total_operations': len(self.results),
            'successful_operations': len([r for r in self.results if r.success]),
            'failed_operations': len([r for r in self.results if not r.success]),
            'operations': []
        }
        
        # Add detailed operation info
        for result in self.results:
            op_info = {
                'name': result.name,
                'duration': result.duration,
                'percentage': (result.duration / total_duration) * 100,
                'success': result.success,
                'metadata': result.metadata
            }
            
            if result.error:
                op_info['error'] = result.error
                
            summary['operations'].append(op_info)
        
        return summary
    
    def get_slowest_operations(self, top_n: int = 5) -> List[Dict]:
        """Get the slowest operations"""
        sorted_results = sorted(
            [r for r in self.results if r.success], 
            key=lambda x: x.duration, 
            reverse=True
        )
        
        return [
            {
                'name': result.name,
                'duration': result.duration,
                'percentage': (result.duration / self.get_total_duration()) * 100,
                'metadata': result.metadata
            }
            for result in sorted_results[:top_n]
        ]
    
    def print_summary(self):
        """Print detailed performance summary"""
        summary = self.get_summary()
        
        print(f"\n📊 Performance Summary for Job {self.job_id}")
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(f"✅ Successful Operations: {summary['successful_operations']}")
        print(f"❌ Failed Operations: {summary['failed_operations']}")
        print(f"\n🔍 Operation Breakdown:")
        
        for op in summary['operations']:
            status = "✅" if op['success'] else "❌"
            print(f"   {status} {op['name']}: {op['duration']:.2f}s ({op['percentage']:.1f}%)")
            
            if op.get('metadata'):
                for key, value in op['metadata'].items():
                    print(f"      📋 {key}: {value}")
        
        print(f"\n🐌 Slowest Operations:")
        slowest = self.get_slowest_operations(3)
        for i, op in enumerate(slowest, 1):
            print(f"   {i}. {op['name']}: {op['duration']:.2f}s ({op['percentage']:.1f}%)")
    
    def get_bottleneck_analysis(self) -> Dict:
        """Analyze bottlenecks and suggest optimizations"""
        summary = self.get_summary()
        slowest = self.get_slowest_operations(3)
        
        analysis = {
            'total_time': summary['total_duration'],
            'bottlenecks': [],
            'recommendations': []
        }
        
        # Identify bottlenecks
        for op in slowest:
            if op['percentage'] > 20:  # Operations taking more than 20% of total time
                analysis['bottlenecks'].append({
                    'operation': op['name'],
                    'duration': op['duration'],
                    'percentage': op['percentage'],
                    'severity': 'high' if op['percentage'] > 50 else 'medium'
                })
        
        # Generate recommendations
        for bottleneck in analysis['bottlenecks']:
            op_name = bottleneck['operation']
            
            if 'whisper' in op_name.lower() or 'transcrib' in op_name.lower():
                analysis['recommendations'].append({
                    'operation': op_name,
                    'suggestion': 'Switch to even smaller Whisper model (base→tiny→tiny.en)',
                    'expected_improvement': '2-3x faster'
                })
            elif 'vibe' in op_name.lower() or 'claude' in op_name.lower():
                analysis['recommendations'].append({
                    'operation': op_name,
                    'suggestion': 'Use shorter prompts or parallel processing',
                    'expected_improvement': '1.5-2x faster'
                })
            elif 'clip' in op_name.lower() or 'ffmpeg' in op_name.lower():
                analysis['recommendations'].append({
                    'operation': op_name,
                    'suggestion': 'Use codec copy mode or reduce clip count',
                    'expected_improvement': '3-5x faster'
                })
            elif 'chunk' in op_name.lower():
                analysis['recommendations'].append({
                    'operation': op_name,
                    'suggestion': 'Reduce chunk count or use simpler chunking',
                    'expected_improvement': '2x faster'
                })
        
        return analysis

# Global profiler storage for tracking across requests
active_profilers: Dict[str, PerformanceProfiler] = {}

def get_profiler(job_id: str) -> PerformanceProfiler:
    """Get or create profiler for job"""
    if job_id not in active_profilers:
        active_profilers[job_id] = PerformanceProfiler(job_id)
    return active_profilers[job_id]

def cleanup_profiler(job_id: str):
    """Clean up profiler when job is done"""
    if job_id in active_profilers:
        del active_profilers[job_id]