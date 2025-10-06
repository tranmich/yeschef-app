"""
Voice Recipe Session Processor
Handles multi-segment voice recording transcription and recipe generation

Created: October 6, 2025
Phase 1: Core voice recording functionality
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

class VoiceSessionProcessor:
    """
    Process multi-segment voice recording sessions into structured recipes
    
    Features:
    - Transcribe audio segments using OpenAI Whisper
    - Combine and auto-edit transcripts
    - Generate structured recipes from verbal descriptions
    - Handle cultural context and language variations
    """
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        """
        Initialize voice session processor
        
        Args:
            openai_client: OpenAI client instance (will create if not provided)
        """
        self.client = openai_client or OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.info("✅ VoiceSessionProcessor initialized")
    
    def process_session(self, session_data: Dict, user_id: int) -> Dict:
        """
        Process complete voice recording session
        
        Args:
            session_data: {
                'session_id': 'uuid',
                'segments': [{'audio_file': file, 'label': str, 'duration_ms': int}],
                'total_duration_ms': int,
                'language_config': {'whisperCode': 'en', 'culture': '...'}
            }
            user_id: User ID for attribution
        
        Returns:
            {
                'combined_transcript': 'full text',
                'auto_edited': 'cleaned text',
                'segments': [...],
                'confidence': 0.85
            }
        """
        logger.info(f"🎤 Processing voice session: {session_data.get('session_id')}")
        logger.info(f"   Segments: {len(session_data.get('segments', []))}")
        logger.info(f"   Total duration: {session_data.get('total_duration_ms', 0) / 1000:.1f}s")
        
        try:
            # Step 1: Transcribe each segment
            segment_transcripts = []
            language_code = session_data.get('language_config', {}).get('whisperCode', 'en')
            
            for idx, segment in enumerate(session_data.get('segments', [])):
                logger.info(f"   📝 Transcribing segment {idx + 1}...")
                
                transcript = self.transcribe_audio(
                    segment['audio_file'],
                    language_code
                )
                
                segment_transcripts.append({
                    'segment_id': idx + 1,
                    'label': segment.get('label'),
                    'text': transcript,
                    'duration_ms': segment.get('duration_ms', 0)
                })
                
                logger.info(f"   ✅ Segment {idx + 1} transcribed ({len(transcript)} chars)")
            
            # Step 2: Combine transcripts
            combined = self._combine_segments(segment_transcripts)
            logger.info(f"   ✅ Combined transcript: {len(combined)} chars")
            
            # Step 3: Auto-edit transcript
            auto_edited = self._auto_edit_transcript(combined)
            logger.info(f"   ✅ Auto-edited transcript: {len(auto_edited)} chars")
            
            # Step 4: Calculate confidence
            confidence = self._calculate_confidence(segment_transcripts)
            
            return {
                'success': True,
                'combined_transcript': combined,
                'auto_edited': auto_edited,
                'segments': segment_transcripts,
                'total_duration_ms': session_data.get('total_duration_ms', 0),
                'confidence': confidence,
                'language': language_code
            }
        
        except Exception as e:
            logger.error(f"❌ Session processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'combined_transcript': '',
                'auto_edited': '',
                'segments': [],
                'confidence': 0.0
            }
    
    def transcribe_audio(self, audio_file, language_code: str = 'en') -> str:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            audio_file: Audio file object (Flask FileStorage) or file-like object
            language_code: ISO language code for Whisper
        
        Returns:
            Transcribed text
        """
        try:
            logger.info(f"🎧 Transcribing audio (language: {language_code})...")
            
            # Handle Flask FileStorage object - need to read bytes
            # OpenAI expects a tuple: (filename, file_content, content_type)
            if hasattr(audio_file, 'read'):
                # It's a file-like object (FileStorage)
                filename = getattr(audio_file, 'filename', 'audio.m4a')
                content_type = getattr(audio_file, 'content_type', 'audio/m4a')
                file_content = audio_file.read()
                
                # Reset stream position if possible
                if hasattr(audio_file, 'seek'):
                    audio_file.seek(0)
                
                logger.info(f"   File: {filename} ({len(file_content)} bytes)")
                
                # Call Whisper API with tuple format
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(filename, file_content, content_type),
                    language=language_code,
                    response_format="text"
                )
            else:
                # It's already a path or proper format
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language_code,
                    response_format="text"
                )
            
            logger.info(f"✅ Transcription complete ({len(transcript)} chars)")
            return transcript
        
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise Exception(f"Transcription error: {str(e)}")
    
    def _combine_segments(self, transcripts: List[Dict]) -> str:
        """
        Intelligently combine segment transcripts
        Handles transitions between segments
        
        Args:
            transcripts: List of segment transcripts
        
        Returns:
            Combined transcript text
        """
        combined_text = []
        
        for i, segment in enumerate(transcripts):
            text = segment['text']
            label = segment.get('label')
            
            # Add section header if labeled
            if label:
                combined_text.append(f"\n[{label}]\n")
            
            # Clean up segment text
            cleaned = self._clean_segment_text(text)
            combined_text.append(cleaned)
            
            # Add spacing between segments
            if i < len(transcripts) - 1:
                combined_text.append("\n\n")
        
        return ''.join(combined_text)
    
    def _clean_segment_text(self, text: str) -> str:
        """Clean up individual segment text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _auto_edit_transcript(self, text: str) -> str:
        """
        Automatic editing before user approval
        - Fix common transcription errors
        - Normalize measurements
        - Clean up filler words
        
        Args:
            text: Combined transcript
        
        Returns:
            Cleaned transcript
        """
        logger.info("✏️ Auto-editing transcript...")
        
        # Remove filler words
        text = re.sub(r'\b(um|uh|like|you know)\b', '', text, flags=re.IGNORECASE)
        
        # Normalize measurements
        replacements = {
            ' cups ': ' cup ',
            ' tablespoons ': ' tablespoon ',
            ' tablespoon ': ' tbsp ',
            ' teaspoons ': ' teaspoon ',
            ' teaspoon ': ' tsp ',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix common fraction transcriptions
        text = text.replace('1 half', '1/2')
        text = text.replace('one half', '1/2')
        text = text.replace('1 quarter', '1/4')
        text = text.replace('one quarter', '1/4')
        text = text.replace('three quarters', '3/4')
        text = text.replace('1 third', '1/3')
        text = text.replace('one third', '1/3')
        text = text.replace('2 thirds', '2/3')
        text = text.replace('two thirds', '2/3')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Single blank lines only
        
        return text
    
    def _calculate_confidence(self, transcripts: List[Dict]) -> float:
        """
        Calculate confidence score based on segment quality
        
        Args:
            transcripts: List of segment transcripts
        
        Returns:
            Confidence score (0-1)
        """
        if not transcripts:
            return 0.0
        
        # Base confidence on transcript length and coherence
        total_chars = sum(len(t['text']) for t in transcripts)
        avg_segment_length = total_chars / len(transcripts)
        
        # Good segments are 100-500 characters
        if avg_segment_length < 50:
            return 0.6  # Too short
        elif avg_segment_length > 1000:
            return 0.7  # Very long (might be rambling)
        else:
            return 0.85  # Good length
    
    def generate_recipe_from_approved_transcript(
        self, 
        transcript: str, 
        metadata: Dict
    ) -> Dict:
        """
        Generate structured recipe from approved transcript
        Uses GPT-4 with contextual understanding
        
        Args:
            transcript: User-approved transcript text
            metadata: {
                'recorded_by': str,
                'culture': str,
                'language': str,
                'duration': int,
                'session_id': str
            }
        
        Returns:
            Structured recipe data
        """
        logger.info("🤖 Generating recipe from transcript...")
        logger.info(f"   Transcript length: {len(transcript)} chars")
        logger.info(f"   Culture context: {metadata.get('culture', 'Unknown')}")
        
        try:
            # Extract title hint from transcript
            title_hint = self._extract_title_hint(transcript)
            logger.info(f"   📝 Detected dish: {title_hint or 'Unknown'}")
            
            # Build contextual prompt
            prompt = self._build_recipe_generation_prompt(
                transcript, 
                title_hint, 
                metadata
            )
            
            # Call GPT-4 (using gpt-4o which supports JSON mode)
            response = self.client.chat.completions.create(
                model="gpt-4o",  # gpt-4o supports json_object response format
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert culinary assistant who converts verbal recipe descriptions into perfectly structured recipes. You understand cultural cooking traditions, vague measurements, and conversational descriptions. You preserve authentic terms while making recipes clear and actionable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            # Parse response
            recipe_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            recipe_data['source'] = 'Voice Recording'
            recipe_data['source_attribution'] = metadata.get('recorded_by', 'Family')
            recipe_data['extraction_method'] = 'voice_session'
            recipe_data['recorded_date'] = datetime.now().isoformat()
            
            # Ensure ingredients and instructions are arrays
            if isinstance(recipe_data.get('ingredients'), str):
                recipe_data['ingredients'] = [recipe_data['ingredients']]
            if isinstance(recipe_data.get('instructions'), str):
                recipe_data['instructions'] = [recipe_data['instructions']]
            
            logger.info(f"✅ Recipe generated: {recipe_data.get('title')}")
            logger.info(f"   Ingredients: {len(recipe_data.get('ingredients', []))}")
            logger.info(f"   Steps: {len(recipe_data.get('instructions', []))}")
            
            return recipe_data
        
        except Exception as e:
            logger.error(f"❌ Recipe generation failed: {e}")
            raise Exception(f"Recipe generation error: {str(e)}")
    
    def _extract_title_hint(self, transcript: str) -> Optional[str]:
        """
        Detect dish name from transcript for context
        
        Args:
            transcript: Full transcript text
        
        Returns:
            Detected dish name or None
        """
        # Common patterns
        patterns = [
            r"(?:this is|making|my mom's|grandma's|family)\s+(.+?)\s+recipe",
            r"(?:how to make|recipe for)\s+(.+?)(?:\.|,|$)",
            r"(?:traditional|authentic)\s+(.+?)(?:\.|,|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript.lower())
            if match:
                dish = match.group(1).strip()
                return dish
        
        return None
    
    def _build_recipe_generation_prompt(
        self, 
        transcript: str, 
        title_hint: Optional[str], 
        metadata: Dict
    ) -> str:
        """
        Build GPT-4 prompt with full context
        
        Args:
            transcript: Verbal recipe description
            title_hint: Detected dish name
            metadata: Recording context
        
        Returns:
            Complete prompt for GPT-4
        """
        prompt = f"""
This is a family recipe described verbally across multiple recording segments.
The speaker recorded in parts using natural conversational language.

RECIPE TYPE: {title_hint or 'Unknown dish'}

CULTURAL CONTEXT:
- Recorded by: {metadata.get('recorded_by', 'Family member')}
- Culture: {metadata.get('culture', 'Unknown')}
- Language: {metadata.get('language', 'English')}
- Recording duration: {metadata.get('duration', 0) / 1000:.0f} seconds

TRANSCRIPT:
{transcript}

INSTRUCTIONS:
Extract a complete, structured recipe with:

1. **Title**: Infer from context if not explicitly stated. Use "{title_hint}" if detected.

2. **Ingredients**: Extract ALL ingredients with quantities
   - Use exact amounts when stated
   - Estimate reasonable quantities for vague amounts ("some", "a bit", "handful")
   - Mark estimates clearly: "~2 cups (estimate)"
   - Preserve cultural terms: "masa harina", "fish sauce", etc.

3. **Instructions**: Create clear step-by-step instructions
   - DO NOT include "Step 1:", "Step 2:" prefixes (numbering added automatically)
   - Write direct action statements: "Heat oil in large pan"
   - Group related micro-steps into clear actions
   - If 20+ micro-steps described, intelligently condense to 8-15 clear steps
   - Preserve critical details: temperatures, times, techniques

4. **Additional Info**:
   - Servings: Estimate if not stated
   - Prep time: Calculate from description
   - Cook time: Estimate from cooking steps
   - Category: breakfast, lunch, dinner, or dessert
   - Cuisine: Based on ingredients and cultural context
   - Tips: Preserve any family wisdom or special techniques mentioned

5. **Cultural Authenticity**:
   - Keep original ingredient names with translations in parentheses when helpful
   - Example: "masa harina (corn flour for tortillas)"
   - Respect traditional preparation methods
   - Preserve family variations

6. **Contextual Intelligence**:
   - Use knowledge of "{title_hint}" recipes to fill gaps
   - Infer standard techniques not explicitly mentioned
   - Estimate temperatures/times based on dish type
   - Add helpful context about traditional preparation

Return ONLY valid JSON in this exact format:
{{
    "title": "Recipe Title",
    "description": "Brief description",
    "ingredients": [
        "2 cups all-purpose flour",
        "1 tsp salt",
        "~1 cup water (estimate)"
    ],
    "instructions": [
        "Mix flour and salt in large bowl",
        "Gradually add water while stirring",
        "Knead until smooth dough forms"
    ],
    "servings": "4-6",
    "prep_time": "15",
    "cook_time": "30",
    "category": "dinner",
    "cuisine": "Italian",
    "tips": [
        "Grandma always let the dough rest for 30 minutes",
        "Dough should be slightly sticky but manageable"
    ]
}}
"""
        return prompt


# Test function for development
def test_voice_processor():
    """Test voice processor with sample data"""
    processor = VoiceSessionProcessor()
    
    # Test transcript generation
    test_transcript = """
    This is my mom's pizza recipe. You need flour, water, yeast, 
    little bit of salt. Let it rise for maybe an hour. Then you 
    spread it out, add sauce, cheese, whatever toppings you want, 
    bake it until it's done.
    """
    
    metadata = {
        'recorded_by': 'Mom',
        'culture': 'Italian-American',
        'language': 'en',
        'duration': 45000
    }
    
    try:
        recipe = processor.generate_recipe_from_approved_transcript(
            test_transcript, 
            metadata
        )
        print("✅ Test successful!")
        print(json.dumps(recipe, indent=2))
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == '__main__':
    # Enable logging for testing
    logging.basicConfig(level=logging.INFO)
    test_voice_processor()
