"""
Performance Benchmark Tests
"""

import pytest
import asyncio
from pathlib import Path

from video_fetcher import VideoFetcher
from persistence import Persistence


def generate_fake_video(idx: int) -> dict:
    """Generate a fake video for testing"""
    return {
        'video_id': f'vid_{idx}',
        'title': f'Video {idx}',
        'url': f'https://youtube.com/watch?v=vid_{idx}',
        'duration': 120 + idx,
        'is_short': False,
        'is_live': False,
        'upload_date': f'202401{idx:02d}'
    }


@pytest.mark.benchmark
def test_filter_1000_videos_performance(benchmark):
    """Benchmark filtering 1000 videos"""
    vf = VideoFetcher("https://example.com/@test")
    videos = [generate_fake_video(i) for i in range(1000)]
    config = {
        'SKIP_SHORTS': True,
        'SKIP_LIVE': True,
        'MIN_VIDEO_DURATION': 60
    }
    
    result = benchmark(vf.filter_videos, videos, config)
    
    assert len(result) > 0
    # Should complete in < 100ms
    assert benchmark.stats['mean'] < 0.1


@pytest.mark.benchmark
def test_database_write_performance(benchmark, tmp_path: Path):
    """Benchmark database write performance"""
    db = Persistence(str(tmp_path / "bench.sqlite"))
    
    def write_videos():
        for i in range(100):
            db.mark_seen(f"vid_{i}", f"Title {i}", 120)
    
    benchmark(write_videos)
    
    # Verify all written
    assert db.get_seen_count() == 100


@pytest.mark.benchmark
def test_database_read_performance(benchmark, tmp_path: Path):
    """Benchmark database read performance"""
    db = Persistence(str(tmp_path / "bench.sqlite"))
    
    # Setup: write 1000 videos
    for i in range(1000):
        db.mark_seen(f"vid_{i}", f"Title {i}", 120)
    
    videos = [generate_fake_video(i) for i in range(1000, 2000)]
    
    # Benchmark get_unseen_videos
    result = benchmark(db.get_unseen_videos, videos)
    
    assert len(result) == len(videos)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_concurrent_operations_throughput():
    """Test throughput with concurrent async operations"""
    import time
    
    async def mock_task(duration: float):
        await asyncio.sleep(duration)
        return True
    
    # Simulate 10 concurrent tasks
    start = time.time()
    tasks = [mock_task(0.1) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    # Should complete in ~0.1s (concurrent) not 1.0s (sequential)
    assert elapsed < 0.2
    assert all(results)
