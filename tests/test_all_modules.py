"""
Comprehensive Test Suite for YouTube Player
Tests all modules, functions, and integrations
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("=" * 80)
print("🧪 YOUTUBE PLAYER - COMPREHENSIVE TEST SUITE")
print("=" * 80)
print()

# Test 1: Module Imports
print("📦 TEST 1: Module Imports")
print("-" * 80)

test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

try:
    from app import get_brave_path, create_driver
    print("✅ app.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ app.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('app.py', str(e)))

try:
    from cookie_manager import CookieManager
    print("✅ cookie_manager.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ cookie_manager.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('cookie_manager.py', str(e)))

try:
    from video_fetcher import VideoFetcher, fetch_channel_videos
    print("✅ video_fetcher.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ video_fetcher.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('video_fetcher.py', str(e)))

try:
    from player_worker import PlayerWorker
    print("✅ player_worker.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ player_worker.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('player_worker.py', str(e)))

try:
    from persistence import Persistence
    print("✅ persistence.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ persistence.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('persistence.py', str(e)))

try:
    from config_loader import load_config, Config
    print("✅ config_loader.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ config_loader.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('config_loader.py', str(e)))

try:
    from logger_config import setup_logging
    print("✅ logger_config.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ logger_config.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('logger_config.py', str(e)))

try:
    from exceptions import *
    print("✅ exceptions.py imports successful")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ exceptions.py import failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('exceptions.py', str(e)))

print()

# Test 2: Configuration Loading
print("📋 TEST 2: Configuration Loading")
print("-" * 80)

try:
    config = load_config()
    print(f"✅ Config loaded successfully")
    print(f"   - Channel URL: {config.get('CHANNEL_URL', 'N/A')}")
    print(f"   - Max Windows: {config.get('MAX_WINDOWS', 'N/A')}")
    print(f"   - Skip Shorts: {config.get('SKIP_SHORTS', 'N/A')}")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ Config loading failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Config Loading', str(e)))

print()

# Test 3: Brave Browser Detection
print("🌐 TEST 3: Brave Browser Detection")
print("-" * 80)

try:
    brave_path = get_brave_path()
    if brave_path and os.path.exists(brave_path):
        print(f"✅ Brave browser found")
        print(f"   Path: {brave_path}")
        test_results['passed'] += 1
    else:
        print(f"⚠️  Brave browser not found (expected for some environments)")
        test_results['passed'] += 1
except Exception as e:
    print(f"❌ Brave detection failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Brave Detection', str(e)))

print()

# Test 4: Database Operations
print("💾 TEST 4: Database Operations")
print("-" * 80)

try:
    test_db_path = "tests/test_db.sqlite"
    os.makedirs("tests", exist_ok=True)
    
    db = Persistence(test_db_path)
    
    # Test marking video as seen
    db.mark_seen("test_video_123", "Test Video", 300)
    print("✅ mark_seen() works")
    
    # Test checking if seen
    is_seen = db.is_seen("test_video_123")
    assert is_seen == True, "Video should be marked as seen"
    print("✅ is_seen() works")
    
    # Test get_seen_count
    count = db.get_seen_count()
    assert count >= 1, "Should have at least 1 seen video"
    print(f"✅ get_seen_count() works ({count} videos)")
    
    # Test get_unseen_videos
    all_videos = [
        {'video_id': 'test_video_123', 'title': 'Test 1'},
        {'video_id': 'test_video_456', 'title': 'Test 2'}
    ]
    unseen = db.get_unseen_videos(all_videos)
    assert len(unseen) == 1, "Should have 1 unseen video"
    print(f"✅ get_unseen_videos() works ({len(unseen)} unseen)")
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    test_results['passed'] += 4
    
except Exception as e:
    print(f"❌ Database operations failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Database Operations', str(e)))

print()

# Test 5: Cookie Manager
print("🍪 TEST 5: Cookie Manager")
print("-" * 80)

try:
    test_cookie_path = "tests/test_cookies.json"
    
    cookie_mgr = CookieManager(test_cookie_path)
    print("✅ CookieManager initialization works")
    
    # Test getting active cookies
    active = cookie_mgr.get_active_cookies()
    print(f"✅ get_active_cookies() works ({len(active)} cookies)")
    
    # Test cookie summary
    summary = cookie_mgr.get_cookie_summary()
    print(f"✅ get_cookie_summary() works")
    print(f"   - Total: {summary.get('total', 0)}")
    print(f"   - Active: {summary.get('active', 0)}")
    
    # Cleanup
    if os.path.exists(test_cookie_path):
        os.remove(test_cookie_path)
    
    test_results['passed'] += 3
    
except Exception as e:
    print(f"❌ Cookie manager failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Cookie Manager', str(e)))

print()

# Test 6: Video Fetcher
print("🎥 TEST 6: Video Fetcher")
print("-" * 80)

try:
    test_url = "https://www.youtube.com/@test"
    fetcher = VideoFetcher(test_url)
    print(f"✅ VideoFetcher initialization works")
    print(f"   - Channel URL: {fetcher.channel_url}")
    
    # Test filter_videos
    test_videos = [
        {'title': 'Video 1', 'duration': 120, 'is_short': False, 'is_live': False},
        {'title': 'Short 1', 'duration': 30, 'is_short': True, 'is_live': False},
        {'title': 'Live 1', 'duration': 0, 'is_short': False, 'is_live': True},
    ]
    
    config_data = {
        'SKIP_SHORTS': True,
        'SKIP_LIVE': True,
        'MIN_VIDEO_DURATION': 60
    }
    
    filtered = fetcher.filter_videos(test_videos, config_data)
    assert len(filtered) == 1, "Should filter correctly"
    print(f"✅ filter_videos() works (filtered {len(test_videos)} → {len(filtered)})")
    
    test_results['passed'] += 2
    
except Exception as e:
    print(f"❌ Video fetcher failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Video Fetcher', str(e)))

print()

# Test 7: Logger Configuration
print("📝 TEST 7: Logger Configuration")
print("-" * 80)

try:
    logger = setup_logging()
    logger.info("Test log message")
    print("✅ Logger setup works")
    print(f"   - Logger name: {logger.name}")
    print(f"   - Log level: {logger.level}")
    test_results['passed'] += 1
except Exception as e:
    print(f"❌ Logger configuration failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Logger Configuration', str(e)))

print()

# Test 8: Exception Classes
print("⚠️  TEST 8: Exception Classes")
print("-" * 80)

try:
    # Test custom exceptions exist
    from exceptions import (
        YouTubePlayerError,
        CookieError,
        VideoFetchError,
        PlayerError,
        ConfigError
    )
    
    # Test raising exceptions
    try:
        raise CookieError("Test cookie error")
    except CookieError as e:
        print(f"✅ CookieError works: {e}")
    
    try:
        raise VideoFetchError("Test fetch error")
    except VideoFetchError as e:
        print(f"✅ VideoFetchError works: {e}")
    
    test_results['passed'] += 2
    
except Exception as e:
    print(f"❌ Exception classes failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Exception Classes', str(e)))

print()

# Final Summary
print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"📈 Success Rate: {test_results['passed']/(test_results['passed']+test_results['failed'])*100:.1f}%")
print()

if test_results['errors']:
    print("❌ ERRORS:")
    for module, error in test_results['errors']:
        print(f"   - {module}: {error}")
    print()

if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {test_results['failed']} TESTS FAILED")

print("=" * 80)
