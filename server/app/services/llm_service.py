"""
Basic LLM service for simple vibe analysis using Claude.
Analyzes transcriptions based on 9 vibes and 6 age groups from frontend.
"""

import os
import json
import asyncio
from typing import Dict, Optional, List
import logging
import random
import time

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("anthropic library not installed. Run: pip install anthropic")

# Gemini imports
try:
    import google.generativeai as genai
except ImportError:
    genai = None  # Will raise in GeminiVibeAnalyzer if used without install

logger = logging.getLogger(__name__)

class SimpleVibeAnalyzer:
    """
    Basic vibe analyzer that works with frontend's 9 vibes and 6 age groups.
    """
    
    # Frontend vibes (must match exactly)
    VIBES = [
        "Happy", "Dramatic", "intense", "Fun", "Inspiring", 
        "Mysterious", "Emotional", "cool", "musical"
    ]
    
    # Frontend age groups (must match exactly)
    AGE_GROUPS = [
        "kids", "teens", "young-adults", "adults", "seniors", "general"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
    
    async def analyze_video_chunks(self, transcription_data: Dict, 
                                 selected_vibe: str, 
                                 selected_age_group: str) -> Dict:
        """
        Analyze video chunks and find the best clips for the selected vibe and age group.
        
        Args:
            transcription_data: Complete transcription with chunks
            selected_vibe: One of the 9 frontend vibes
            selected_age_group: One of the 6 frontend age groups
            
        Returns:
            Simple analysis with ranked clips
        """
        # Validate inputs
        if selected_vibe not in self.VIBES:
            logger.warning(f"Unknown vibe: {selected_vibe}, defaulting to 'Happy'")
            selected_vibe = "Happy"
            
        if selected_age_group not in self.AGE_GROUPS:
            logger.warning(f"Unknown age group: {selected_age_group}, defaulting to 'general'")
            selected_age_group = "general"
        
        # Get chunks from transcription
        chunks = transcription_data.get('chunks', [])
        if not chunks:
            return self._empty_result()
        
        # Filter successful chunks with good transcription
        valid_chunks = [
            chunk for chunk in chunks 
            if chunk.get('success') and 
            chunk.get('transcription', {}).get('text', '').strip() and
            len(chunk.get('transcription', {}).get('text', '')) > 4
        ]
        
        # LIMIT TO FIRST 3 CHUNKS TO SAVE CREDITS
        if len(valid_chunks) > 3:
            logger.info(f"Limiting analysis to first 3 chunks (out of {len(valid_chunks)}) to save API credits")
            valid_chunks = valid_chunks[:3]
        
        if not valid_chunks:
            return self._empty_result()
        
        # Analyze chunks for the specific vibe and age group
        analyzed_chunks = await self._analyze_chunks_for_vibe(
            valid_chunks, selected_vibe, selected_age_group
        )
        
        # Rank and return top clips
        top_clips = self._rank_clips(analyzed_chunks, selected_vibe, selected_age_group)
        
        return {
            'selected_vibe': selected_vibe,
            'selected_age_group': selected_age_group,
            'total_chunks_analyzed': len(valid_chunks),
            'clips_found': len(top_clips),
            'top_clips': top_clips[:5],  # Return top 5 clips
            'status': 'success'
        }
    
    async def _analyze_chunks_for_vibe(self, chunks: List[Dict], 
                                     target_vibe: str, 
                                     target_age_group: str) -> List[Dict]:
        """Analyze each chunk for the target vibe and age group."""
        analyzed_chunks = []
        
        # Process chunks in batches to avoid API limits
        batch_size = 3
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_results = await self._analyze_chunk_batch(batch, target_vibe, target_age_group)
            analyzed_chunks.extend(batch_results)
        
        return analyzed_chunks
    
    async def _analyze_chunk_batch(self, chunks: List[Dict], 
                                 target_vibe: str, 
                                 target_age_group: str) -> List[Dict]:
        """Analyze a batch of chunks."""
        results = []
        
        for chunk in chunks:
            text = chunk.get('transcription', {}).get('text', '')
            start_time = chunk.get('start_time', 0)
            end_time = chunk.get('end_time', 0)
            
            analysis = await self._analyze_single_chunk(
                text, start_time, end_time, target_vibe, target_age_group
            )
            
            if analysis:
                results.append({
                    'chunk_id': chunk.get('id'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'text': text,
                    'analysis': analysis
                })
            await asyncio.sleep(1) # Add a 1-second delay to respect rate limits
        
        return results
    
    async def _analyze_single_chunk(self, text: str, start_time: float, 
                                  end_time: float, target_vibe: str, 
                                  target_age_group: str) -> Optional[Dict]:
        """Analyze a single chunk for vibe match."""
        
        prompt = f"""
Analyze this video segment text to see how well it matches the target vibe and age group.

Target Vibe: {target_vibe}
Target Age Group: {target_age_group}

Segment (from {start_time:.1f}s to {end_time:.1f}s):
"{text}"

Rate this segment on:
1. How well it matches the "{target_vibe}" vibe (0-100)
2. How suitable it is for "{target_age_group}" audience (0-100)
3. How good it would be as a short clip (0-100)

Respond in this exact JSON format:
{{
    "vibe_match_score": 0-100,
    "age_group_match_score": 0-100,
    "clip_potential_score": 0-100,
    "overall_score": 0-100,
    "reason": "brief explanation of why this does/doesn't match",
    "best_moment": "describe the most interesting part if any"
}}
"""
        
        try:
            response = await self._call_claude(prompt, max_tokens=500)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Error analyzing chunk: {e}")
            return None
    
    async def _call_claude(self, prompt: str, max_tokens: int = 500) -> str:
        """Make API call to Claude."""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,  # Low temperature for consistent scoring
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            # Handle different response types
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content[0])
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _parse_response(self, response: str) -> Optional[Dict]:
        """Parse Claude's JSON response."""
        try:
            # Find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['vibe_match_score', 'age_group_match_score', 
                                 'clip_potential_score', 'overall_score']
                if all(field in parsed for field in required_fields):
                    return parsed
            
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse response: {e}")
            return None
    
    def _rank_clips(self, analyzed_chunks: List[Dict], 
                   target_vibe: str, target_age_group: str) -> List[Dict]:
        """Rank clips by their scores and return the best ones."""
        # Filter out chunks without analysis
        valid_chunks = [
            chunk for chunk in analyzed_chunks 
            if chunk.get('analysis') and chunk['analysis'].get('overall_score', 0) > 30
        ]
        
        # Sort by overall score (descending)
        valid_chunks.sort(
            key=lambda x: x.get('analysis', {}).get('overall_score', 0), 
            reverse=True
        )
        
        # Format for frontend
        ranked_clips = []
        for i, chunk in enumerate(valid_chunks):
            analysis = chunk.get('analysis', {})
            ranked_clips.append({
                'rank': i + 1,
                'start_time': chunk.get('start_time'),
                'end_time': chunk.get('end_time'),
                'duration': chunk.get('duration'),
                'title': f"{target_vibe} Clip {i + 1}",
                'text_preview': chunk.get('text', '')[:100] + "..." if len(chunk.get('text', '')) > 100 else chunk.get('text', ''),
                'scores': {
                    'vibe_match': analysis.get('vibe_match_score', 0),
                    'age_group_match': analysis.get('age_group_match_score', 0),
                    'clip_potential': analysis.get('clip_potential_score', 0),
                    'overall': analysis.get('overall_score', 0)
                },
                'reason': analysis.get('reason', ''),
                'best_moment': analysis.get('best_moment', ''),
                'recommended_for': target_age_group,
                'vibe': target_vibe
            })
        
        return ranked_clips
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'selected_vibe': '',
            'selected_age_group': '',
            'total_chunks_analyzed': 0,
            'clips_found': 0,
            'top_clips': [],
            'status': 'no_content',
            'message': 'No valid transcription chunks found for analysis'
        }


class GeminiVibeAnalyzer:
    """
    Vibe analyzer using Google Gemini 2.5 Pro API (default: models/gemini-2.5-pro-latest).
    Matches interface of SimpleVibeAnalyzer for parallel use.
    Set GEMINI_MODEL in your .env to override.
    """
    VIBES = SimpleVibeAnalyzer.VIBES
    AGE_GROUPS = SimpleVibeAnalyzer.AGE_GROUPS

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash-latest"):
        if genai is None:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        self.model = model
        # Debug: List available models (uncomment for troubleshooting)
        # try:
        #     models = genai.list_models()
        #     for m in models:
        #         print(f"[Gemini] Available model: {m.name}")
        # except Exception as e:
        #     print(f"[Gemini] Could not list models: {e}")
        self.gemini_model = genai.GenerativeModel(self.model)

    async def analyze_video_chunks(self, transcription_data: Dict, selected_vibe: str, selected_age_group: str) -> Dict:
        if selected_vibe not in self.VIBES:
            logger.warning(f"Unknown vibe: {selected_vibe}, defaulting to 'Happy'")
            selected_vibe = "Happy"
        if selected_age_group not in self.AGE_GROUPS:
            logger.warning(f"Unknown age group: {selected_age_group}, defaulting to 'general'")
            selected_age_group = "general"
        chunks = transcription_data.get('chunks', [])
        if not chunks:
            return self._empty_result()
        valid_chunks = [
            chunk for chunk in chunks
            if chunk.get('success') and chunk.get('transcription', {}).get('text', '').strip() and len(chunk.get('transcription', {}).get('text', '')) > 4
        ]
        if len(valid_chunks) > 3:
            logger.info(f"Limiting analysis to first 3 chunks (out of {len(valid_chunks)}) to save API credits")
            valid_chunks = valid_chunks[:3]
        if not valid_chunks:
            return self._empty_result()
        analyzed_chunks = await self._analyze_chunks_for_vibe(valid_chunks, selected_vibe, selected_age_group)
        top_clips = self._rank_clips(analyzed_chunks, selected_vibe, selected_age_group)
        return {
            'selected_vibe': selected_vibe,
            'selected_age_group': selected_age_group,
            'total_chunks_analyzed': len(valid_chunks),
            'clips_found': len(top_clips),
            'top_clips': top_clips[:5],
            'status': 'success'
        }

    async def _analyze_chunks_for_vibe(self, chunks: List[Dict], target_vibe: str, target_age_group: str) -> List[Dict]:
        analyzed_chunks = []
        batch_size = 3
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_results = await self._analyze_chunk_batch(batch, target_vibe, target_age_group)
            analyzed_chunks.extend(batch_results)
        return analyzed_chunks

    async def _analyze_chunk_batch(self, chunks: List[Dict], target_vibe: str, target_age_group: str) -> List[Dict]:
        results = []
        for chunk in chunks:
            text = chunk.get('transcription', {}).get('text', '')
            start_time = chunk.get('start_time', 0)
            end_time = chunk.get('end_time', 0)
            analysis = await self._analyze_single_chunk(text, start_time, end_time, target_vibe, target_age_group)
            if analysis:
                results.append({
                    'chunk_id': chunk.get('id'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'text': text,
                    'analysis': analysis
                })
            await asyncio.sleep(1) # Add a 1-second delay to respect rate limits
        return results

    async def _analyze_single_chunk(self, text: str, start_time: float, end_time: float, target_vibe: str, target_age_group: str) -> Optional[Dict]:
        # Log input size and prompt
        logger.info(f"[Gemini] Analyzing chunk {start_time:.1f}-{end_time:.1f}s, text length: {len(text)}")
        # Truncate text if too long (e.g., >2000 chars)
        max_text_len = 2000
        if len(text) > max_text_len:
            logger.warning(f"[Gemini] Truncating chunk text from {len(text)} to {max_text_len} chars")
            text = text[:max_text_len]
        prompt = f"""
Analyze this video segment text to see how well it matches the target vibe and age group.

Target Vibe: {target_vibe}
Target Age Group: {target_age_group}

Segment (from {start_time:.1f}s to {end_time:.1f}s):
"{text}"

Rate this segment on:
1. How well it matches the \"{target_vibe}\" vibe (0-100)
2. How suitable it is for \"{target_age_group}\" audience (0-100)
3. How good it would be as a short clip (0-100)

Respond in this exact JSON format:
{{
    "vibe_match_score": 0-100,
    "age_group_match_score": 0-100,
    "clip_potential_score": 0-100,
    "overall_score": 0-100,
    "reason": "brief explanation of why this does/doesn't match",
    "best_moment": "describe the most interesting part if any"
}}
"""
        logger.info(f"[Gemini] Prompt (first 500 chars): {prompt[:500]}")
        import asyncio
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self._call_gemini, prompt),
                timeout=60
            )
            return self._parse_response(response)
        except asyncio.TimeoutError:
            logger.error("[Gemini] Vibe analysis timed out for chunk {start_time}-{end_time}s")
            return {
                "vibe_match_score": 0,
                "age_group_match_score": 0,
                "clip_potential_score": 0,
                "overall_score": 0,
                "reason": "Timeout during Gemini analysis.",
                "best_moment": ""
            }
        except Exception as e:
            logger.error(f"[Gemini] Error analyzing chunk: {e}")
            return None

    def _call_gemini(self, prompt: str) -> str:
        max_retries = 5
        base_delay = 2  # seconds
        print(f"Using Gemini API Key: {self.api_key}") # Print the key for debugging
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Gemini generate_content failed: {e}")
                    raise

    def _parse_response(self, response: str) -> Optional[Dict]:
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                required_fields = ['vibe_match_score', 'age_group_match_score', 'clip_potential_score', 'overall_score']
                if all(field in parsed for field in required_fields):
                    return parsed
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Gemini response: {e}")
            return None

    def _rank_clips(self, analyzed_chunks: List[Dict], target_vibe: str, target_age_group: str) -> List[Dict]:
        valid_chunks = [
            chunk for chunk in analyzed_chunks
            if chunk.get('analysis') and chunk['analysis'].get('overall_score', 0) > 30
        ]
        valid_chunks.sort(key=lambda x: x.get('analysis', {}).get('overall_score', 0), reverse=True)
        ranked_clips = []
        for i, chunk in enumerate(valid_chunks):
            analysis = chunk.get('analysis', {})
            ranked_clips.append({
                'rank': i + 1,
                'start_time': chunk.get('start_time'),
                'end_time': chunk.get('end_time'),
                'duration': chunk.get('duration'),
                'title': f"{target_vibe} Clip {i + 1}",
                'text_preview': chunk.get('text', '')[:100] + "..." if len(chunk.get('text', '')) > 100 else chunk.get('text', ''),
                'scores': {
                    'vibe_match': analysis.get('vibe_match_score', 0),
                    'age_group_match': analysis.get('age_group_match_score', 0),
                    'clip_potential': analysis.get('clip_potential_score', 0),
                    'overall': analysis.get('overall_score', 0)
                },
                'reason': analysis.get('reason', ''),
                'best_moment': analysis.get('best_moment', ''),
                'recommended_for': target_age_group,
                'vibe': target_vibe
            })
        return ranked_clips

    def _empty_result(self) -> Dict:
        return {
            'selected_vibe': '',
            'selected_age_group': '',
            'total_chunks_analyzed': 0,
            'clips_found': 0,
            'top_clips': [],
            'status': 'no_content',
            'message': 'No valid transcription chunks found for analysis'
        }


class VibeAnalysisManager:
    """
    Simple manager for coordinating vibe analysis workflow.
    """
    
    def __init__(self, vibe_analyzer: SimpleVibeAnalyzer):
        self.vibe_analyzer = vibe_analyzer
    
    async def analyze_video_vibe(self, transcription_result: Dict, 
                               project_context: Optional[Dict] = None) -> Dict:
        """
        Simple vibe analysis workflow.
        
        Args:
            transcription_result: Result from whisper transcription
            project_context: Contains selected_vibe and selected_age_group
            
        Returns:
            Analysis results with ranked clips
        """
        try:
            # Extract vibe and age group from project context
            logger.info(f"🔍 Project context received: {project_context}")
            
            if not project_context:
                return {
                    'error': 'No project context provided',
                    'status': 'failed'
                }
            
            selected_vibe = project_context.get('selected_vibe', 'Happy')
            selected_age_group = project_context.get('selected_age_group', 'general')
            
            logger.info(f"🎭 Selected vibe: {selected_vibe}, Age group: {selected_age_group}")
            
            # Perform analysis
            result = await self.vibe_analyzer.analyze_video_chunks(
                transcription_result, selected_vibe, selected_age_group
            )
            
            return {
                'vibe_analysis': result,
                'transcription_stats': {
                    'total_chunks': len(transcription_result.get('chunks', [])),
                    'successful_chunks': len([
                        c for c in transcription_result.get('chunks', []) 
                        if c.get('success')
                    ]),
                    'total_duration': transcription_result.get('processing_stats', {}).get('total_duration', 0)
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error in vibe analysis workflow: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }

def list_gemini_models(api_key=None):
    """Print available Gemini model names for the configured API key."""
    try:
        import google.generativeai as genai
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        models = genai.list_models()
        print("[Gemini] Available models:")
        for m in models:
            print(f"- {m.name}")
    except Exception as e:
        print(f"[Gemini] Could not list models: {e}")