"""
🎥 YouTube Recipe Extractor
============================

Extracts recipe content from YouTube cooking videos using:
1. YouTube Data API v3 for video metadata and descriptions
2. youtube-transcript-api for captions/transcripts
3. Intelligent text combination for AI parsing

Author: GitHub Copilot & YesChef Team
Date: October 2025
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests

# YouTube API imports
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logging.warning("google-api-python-client not installed. Install with: pip install google-api-python-client")

# Transcript API import
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    logging.warning("youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")

# Duration parsing
try:
    import isodate
    ISODATE_AVAILABLE = True
except ImportError:
    ISODATE_AVAILABLE = False
    logging.warning("isodate not installed. Install with: pip install isodate")

logger = logging.getLogger(__name__)


@dataclass
class YouTubeVideoData:
    """Structured YouTube video data"""
    video_id: str
    title: str
    description: str
    channel: str
    duration_seconds: int
    view_count: int
    published_at: str
    transcript: Optional[str] = None
    captions_available: bool = False
    language: str = 'en'
    thumbnail_url: Optional[str] = None
    channel_id: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @property
    def duration_formatted(self) -> str:
        """Format duration in seconds to human-readable format (e.g., '15:30' or '1:02:15')"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        secs = self.duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['duration_formatted'] = self.duration_formatted
        return data


class YouTubeRecipeExtractor:
    """
    Extract recipe information from YouTube cooking videos
    
    Features:
    - Supports multiple YouTube URL formats
    - Fetches video metadata via YouTube Data API v3
    - Retrieves transcripts/captions when available
    - Combines all text sources for optimal AI parsing
    - Graceful degradation when transcripts unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube extractor
        
        Args:
            api_key: YouTube Data API v3 key. If None, reads from YOUTUBE_API_KEY env var
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError(
                "YouTube API dependencies not installed. "
                "Install with: pip install google-api-python-client"
            )
        
        if not TRANSCRIPT_API_AVAILABLE:
            logger.warning(
                "Transcript API not available. Videos without descriptions may fail. "
                "Install with: pip install youtube-transcript-api"
            )
        
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("✅ YouTube API client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize YouTube API client: {e}")
                raise
        else:
            raise ValueError(
                "YouTube API key not provided. "
                "Set YOUTUBE_API_KEY environment variable or pass api_key parameter"
            )
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&feature=share
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string or None if not found
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
            r'm\.youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"✅ Extracted video ID: {video_id}")
                return video_id
        
        logger.warning(f"⚠️ Could not extract video ID from URL: {url}")
        return None
    
    def get_video_metadata(self, video_id: str) -> Optional[YouTubeVideoData]:
        """
        Fetch video metadata using YouTube Data API v3
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            YouTubeVideoData object or None if fetch fails
        """
        if not self.youtube:
            logger.error("❌ YouTube API client not initialized")
            return None
        
        try:
            # Request video details
            logger.info(f"🔍 Fetching metadata for video: {video_id}")
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.warning(f"⚠️ No video found with ID: {video_id}")
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video.get('statistics', {})
            
            # Parse duration
            duration_seconds = 0
            if ISODATE_AVAILABLE:
                try:
                    duration = isodate.parse_duration(content_details['duration'])
                    duration_seconds = int(duration.total_seconds())
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse duration: {e}")
            
            # Get best quality thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = None
            for quality in ['maxres', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality]['url']
                    break
            
            video_data = YouTubeVideoData(
                video_id=video_id,
                title=snippet['title'],
                description=snippet.get('description', ''),
                channel=snippet['channelTitle'],
                duration_seconds=duration_seconds,
                view_count=int(statistics.get('viewCount', 0)),
                published_at=snippet['publishedAt'],
                thumbnail_url=thumbnail_url
            )
            
            logger.info(f"✅ Successfully fetched metadata for: {video_data.title}")
            logger.info(f"   Channel: {video_data.channel}")
            logger.info(f"   Duration: {duration_seconds}s")
            logger.info(f"   Views: {video_data.view_count:,}")
            
            return video_data
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching video metadata: {e}")
            return None
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> Optional[str]:
        """
        Get video transcript/captions using youtube-transcript-api
        
        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (default: ['en', 'en-US'])
            
        Returns:
            Full transcript as single string, or None if unavailable
        """
        if not TRANSCRIPT_API_AVAILABLE:
            logger.warning("⚠️ Transcript API not available")
            return None
        
        if languages is None:
            languages = ['en', 'en-US', 'en-GB']
        
        try:
            logger.info(f"🎬 Attempting to fetch transcript for: {video_id}")
            
            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id, languages=languages)
            
            # Extract text from transcript snippets
            full_text = ' '.join([snippet.text for snippet in transcript_data.snippets])
            
            logger.info(f"✅ Successfully fetched transcript ({len(full_text)} chars)")
            return full_text
                
        except TranscriptsDisabled:
            logger.warning(f"⚠️ Transcripts are disabled for video: {video_id}")
        except NoTranscriptFound:
            logger.warning(f"⚠️ No transcript found for video: {video_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not retrieve transcript: {e}")
        
        return None
    
    def combine_text_sources(self, video_data: YouTubeVideoData) -> str:
        """
        Intelligently combine title, description, and transcript for AI parsing
        
        Prioritizes:
        1. Title (most important for recipe name)
        2. Description (often contains ingredients list)
        3. Transcript (detailed cooking instructions)
        
        Args:
            video_data: YouTubeVideoData object with all video information
            
        Returns:
            Combined text optimized for recipe extraction
        """
        parts = []
        
        # Title - most important identifier
        parts.append(f"=== VIDEO TITLE ===")
        parts.append(video_data.title)
        parts.append("")
        
        # Channel - helps with context
        parts.append(f"=== CHANNEL ===")
        parts.append(video_data.channel)
        parts.append("")
        
        # Description - often has ingredients
        if video_data.description and len(video_data.description.strip()) > 0:
            parts.append(f"=== VIDEO DESCRIPTION ===")
            parts.append(video_data.description)
            parts.append("")
        
        # Transcript - detailed instructions
        if video_data.transcript and len(video_data.transcript.strip()) > 0:
            parts.append(f"=== VIDEO TRANSCRIPT (spoken content) ===")
            parts.append(video_data.transcript)
        
        combined = '\n'.join(parts)
        
        logger.info(f"📝 Combined text length: {len(combined)} characters")
        logger.info(f"   - Has description: {bool(video_data.description)}")
        logger.info(f"   - Has transcript: {bool(video_data.transcript)}")
        
        return combined
    
    def extract_recipe_content(self, url: str) -> Dict:
        """
        Main extraction method - gets all available content from YouTube video
        
        This is the primary interface method. It orchestrates:
        1. Video ID extraction
        2. Metadata fetching
        3. Transcript retrieval
        4. Text combination
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dict with:
                - success: bool
                - video_data: YouTubeVideoData object
                - combined_text: str (ready for AI parsing)
                - source_url: str
                - error: str (if failed)
        """
        logger.info(f"🎥 Starting YouTube recipe extraction for: {url}")
        
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return {
                'success': False,
                'error': 'Invalid YouTube URL - could not extract video ID',
                'source_url': url
            }
        
        # Get metadata
        video_data = self.get_video_metadata(video_id)
        if not video_data:
            return {
                'success': False,
                'error': 'Could not fetch video information - video may be private or deleted',
                'source_url': url
            }
        
        # Get transcript (optional - gracefully handles failure)
        transcript = self.get_transcript(video_id)
        video_data.transcript = transcript
        video_data.captions_available = transcript is not None
        
        # Warn if no transcript available
        if not transcript:
            logger.warning("⚠️ No transcript available - relying on description only")
            if not video_data.description or len(video_data.description.strip()) < 50:
                return {
                    'success': False,
                    'error': 'Video has no transcript or description - cannot extract recipe',
                    'source_url': url,
                    'video_data': video_data
                }
        
        # Combine all text sources
        combined_text = self.combine_text_sources(video_data)
        
        logger.info("✅ Successfully extracted YouTube content")
        logger.info(f"   Title: {video_data.title}")
        logger.info(f"   Channel: {video_data.channel}")
        logger.info(f"   Text length: {len(combined_text)} chars")
        
        return {
            'success': True,
            'video_data': video_data,
            'combined_text': combined_text,
            'source_url': url,
            'has_transcript': video_data.captions_available
        }
    
    def is_youtube_url(self, url: str) -> bool:
        """
        Check if URL is from YouTube
        
        Args:
            url: URL string to check
            
        Returns:
            True if URL is from YouTube
        """
        youtube_domains = [
            'youtube.com',
            'youtu.be',
            'm.youtube.com',
            'www.youtube.com'
        ]
        
        url_lower = url.lower()
        return any(domain in url_lower for domain in youtube_domains)


# Convenience function for quick testing
def test_extraction(url: str):
    """
    Test YouTube extraction on a single URL
    
    Usage:
        python youtube_recipe_extractor.py "https://youtube.com/watch?v=abc123"
    """
    print(f"\n🎥 Testing YouTube Recipe Extractor")
    print(f"URL: {url}\n")
    
    try:
        extractor = YouTubeRecipeExtractor()
        result = extractor.extract_recipe_content(url)
        
        if result['success']:
            print("✅ Extraction successful!")
            print(f"\nVideo Data:")
            video_data = result['video_data']
            print(f"  Title: {video_data.title}")
            print(f"  Channel: {video_data.channel}")
            print(f"  Duration: {video_data.duration_seconds}s")
            print(f"  Has Transcript: {video_data.captions_available}")
            print(f"\nCombined Text Preview (first 500 chars):")
            print(result['combined_text'][:500])
            print("...")
        else:
            print(f"❌ Extraction failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        test_extraction(sys.argv[1])
    else:
        print("Usage: python youtube_recipe_extractor.py <youtube_url>")
        print("\nExample:")
        print('  python youtube_recipe_extractor.py "https://youtube.com/watch?v=abc123"')
