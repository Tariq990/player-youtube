"""
Integration Tests
Tests that interact with real external services (YouTube, yt-dlp)
"""

import pytest
from video_fetcher import VideoFetcher, fetch_channel_videos


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_youtube_channel_fetch():
    """Test fetching from a real YouTube channel (requires network)"""
    # Use a stable test channel
    channel_url = "https://www.youtube.com/@YouTube"
    
    fetcher = VideoFetcher(channel_url)
    videos = await fetcher.fetch_videos(max_videos=5)
    
    assert len(videos) > 0, "Should fetch at least one video"
    
    # Validate video structure
    for video in videos:
        assert 'video_id' in video
        assert 'title' in video
        assert 'duration' in video
        assert 'url' in video
        assert video['url'].startswith('https://www.youtube.com/watch?v=')


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_video_filtering():
    """Test filtering with real data"""
    channel_url = "https://www.youtube.com/@YouTube"
    
    config = {
        'SKIP_SHORTS': True,
        'SKIP_LIVE': True,
        'MIN_VIDEO_DURATION': 60
    }
    
    videos = await fetch_channel_videos(channel_url, config, max_videos=10)
    
    # All videos should meet criteria
    for video in videos:
        assert video.get('duration', 0) >= 60, "All videos should be >= 60s"
        if video.get('is_short'):
            pytest.fail("Shorts should be filtered out")
        if video.get('is_live'):
            pytest.fail("Live videos should be filtered out")


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_yt_dlp_timeout():
    """Test that yt-dlp timeout works correctly"""
    import time
    
    channel_url = "https://www.youtube.com/@YouTube"
    fetcher = VideoFetcher(channel_url)
    
    start = time.time()
    videos = await fetcher.fetch_videos(max_videos=100)
    elapsed = time.time() - start
    
    # Should complete within timeout (120s default)
    assert elapsed < 125, "Should respect timeout"
    assert len(videos) > 0, "Should fetch some videos"
