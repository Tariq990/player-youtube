"""
Video Fetcher - Fetch videos from YouTube channel.
Uses yt-dlp to extract video metadata.
"""

# Standard library imports
import json
import logging
import subprocess
from typing import Dict, List

# Get logger
logger = logging.getLogger(__name__)


class VideoFetcher:
    """Fetch videos from YouTube channel using yt-dlp"""
    
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
    
    def fetch_videos(self, max_videos: int = 50) -> List[Dict]:
        """
        Fetch videos from channel
        Returns list of video objects
        """
        logger.info(f"Fetching videos from channel: {self.channel_url}")
        print(f"\n🔍 Fetching videos from: {self.channel_url}")
        
        try:
            # Use yt-dlp to get video list - add /videos to get actual videos
            video_url = self.channel_url
            if not video_url.endswith('/videos'):
                video_url = video_url.rstrip('/') + '/videos'
            
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--dump-single-json',
                '--playlist-end', str(max_videos),
                video_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp error: {result.stderr}")
                print(f"❌ yt-dlp error: {result.stderr}")
                return []
            
            data = json.loads(result.stdout)
            
            # Handle nested structure
            entries = data.get('entries', [])
            
            # If we got playlists, dig deeper
            if entries and isinstance(entries[0], dict) and entries[0].get('_type') == 'playlist':
                # Flatten nested playlists
                all_videos = []
                for playlist in entries:
                    playlist_entries = playlist.get('entries', [])
                    all_videos.extend(playlist_entries)
                entries = all_videos
            
            videos = []
            for entry in entries:
                if not entry:
                    continue
                
                # Skip if it's still a playlist
                if entry.get('_type') == 'playlist':
                    continue
                
                video = {
                    'video_id': entry.get('id', ''),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                    'title': entry.get('title', 'Unknown'),
                    'duration': entry.get('duration', 0),
                    'is_live': entry.get('is_live', False),
                    'upload_date': entry.get('upload_date', ''),
                }
                
                # Check if it's a short (< 60 seconds typically)
                video['is_short'] = video['duration'] < 60 if video['duration'] else False
                
                videos.append(video)
            
            print(f"✅ Found {len(videos)} videos")
            return videos
            
        except subprocess.TimeoutExpired:
            print("❌ Timeout fetching videos")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error fetching videos: {e}")
            return []
    
    def filter_videos(self, videos: List[Dict], config: Dict) -> List[Dict]:
        """Filter videos based on config"""
        filtered = []
        
        skip_shorts = config.get('SKIP_SHORTS', True)
        skip_live = config.get('SKIP_LIVE', True)
        min_duration = config.get('MIN_VIDEO_DURATION', 10)
        
        for video in videos:
            # Skip shorts
            if skip_shorts and video.get('is_short', False):
                print(f"⏭️  Skipping short: {video['title']}")
                continue
            
            # Skip live
            if skip_live and video.get('is_live', False):
                print(f"⏭️  Skipping live: {video['title']}")
                continue
            
            # Skip too short videos
            if video.get('duration', 0) < min_duration:
                print(f"⏭️  Skipping (too short): {video['title']}")
                continue
            
            filtered.append(video)
        
        # Sort by upload_date - OLDEST FIRST
        filtered.sort(key=lambda x: x.get('upload_date', '0'), reverse=False)
        
        print(f"✅ Filtered to {len(filtered)} videos (sorted oldest first)")
        return filtered


def fetch_channel_videos(channel_url: str, config: Dict, max_videos: int = 50) -> List[Dict]:
    """
    Convenience function to fetch and filter videos
    """
    fetcher = VideoFetcher(channel_url)
    videos = fetcher.fetch_videos(max_videos)
    return fetcher.filter_videos(videos, config)
