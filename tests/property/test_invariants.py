"""
Property-Based Tests using Hypothesis
Tests invariants and edge cases automatically
"""

import pytest
from hypothesis import given, strategies as st, assume

from video_fetcher import VideoFetcher


@given(
    duration=st.integers(min_value=0, max_value=86400),
    is_short=st.booleans(),
    is_live=st.booleans(),
)
def test_video_filtering_invariants(duration, is_short, is_live):
    """Test that filtering logic is consistent with any inputs"""
    video = {
        'title': 'Test Video',
        'video_id': 'test123',
        'duration': duration,
        'is_short': is_short,
        'is_live': is_live,
        'upload_date': '20240101'
    }
    
    vf = VideoFetcher("https://example.com")
    config = {
        'SKIP_SHORTS': True,
        'SKIP_LIVE': True,
        'MIN_VIDEO_DURATION': 60
    }
    
    result = vf.filter_videos([video], config)
    
    # Invariant 1: If live and skip_live, must be filtered
    if is_live and config['SKIP_LIVE']:
        assert len(result) == 0, "Live videos should be filtered when SKIP_LIVE=True"
    
    # Invariant 2: If short and skip_shorts, must be filtered
    if is_short and config['SKIP_SHORTS']:
        assert len(result) == 0, "Shorts should be filtered when SKIP_SHORTS=True"
    
    # Invariant 3: If duration too short, must be filtered
    if duration < config['MIN_VIDEO_DURATION']:
        assert len(result) == 0, "Videos shorter than MIN_VIDEO_DURATION should be filtered"
    
    # Invariant 4: Result can't have more items than input
    assert len(result) <= 1, "Can't create videos out of thin air"


@given(
    videos=st.lists(
        st.fixed_dictionaries({
            'title': st.text(min_size=1, max_size=50),
            'video_id': st.text(min_size=1, max_size=20),
            'duration': st.integers(min_value=0, max_value=86400),
            'is_short': st.booleans(),
            'is_live': st.booleans(),
            'upload_date': st.text(min_size=8, max_size=8, alphabet='0123456789')
        }),
        min_size=0,
        max_size=100
    )
)
def test_filtering_preserves_order(videos):
    """Test that filtering preserves relative ordering"""
    vf = VideoFetcher("https://example.com")
    config = {
        'SKIP_SHORTS': False,  # Don't skip anything
        'SKIP_LIVE': False,
        'MIN_VIDEO_DURATION': 0
    }
    
    result = vf.filter_videos(videos, config)
    
    # After sorting by upload_date, order should be consistent
    sorted_dates = [v['upload_date'] for v in result]
    assert sorted_dates == sorted(sorted_dates), "Videos should be sorted by upload_date"


@given(
    min_duration=st.integers(min_value=0, max_value=3600),
    video_duration=st.integers(min_value=0, max_value=7200)
)
def test_min_duration_boundary(min_duration, video_duration):
    """Test boundary conditions for minimum duration"""
    video = {
        'title': 'Test',
        'video_id': 'test',
        'duration': video_duration,
        'is_short': False,
        'is_live': False,
        'upload_date': '20240101'
    }
    
    vf = VideoFetcher("url")
    config = {
        'SKIP_SHORTS': False,
        'SKIP_LIVE': False,
        'MIN_VIDEO_DURATION': min_duration
    }
    
    result = vf.filter_videos([video], config)
    
    # Invariant: video passes iff duration >= min_duration
    if video_duration >= min_duration:
        assert len(result) == 1, f"Video with duration {video_duration} should pass min {min_duration}"
    else:
        assert len(result) == 0, f"Video with duration {video_duration} should fail min {min_duration}"
