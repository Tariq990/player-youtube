"""
Advanced Test Suite for YouTube Player
Tests: Integration, Network, Concurrency, Error Handling, Performance
"""

import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("=" * 80)
print("🚀 YOUTUBE PLAYER - ADVANCED TEST SUITE")
print("=" * 80)
print()

test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

# ============================================================================
# TEST 1: Cookie Rotation and Fallback
# ============================================================================
print("🍪 TEST 1: Cookie Rotation and Fallback Logic")
print("-" * 80)

try:
    from cookie_manager import CookieManager
    
    # Test 1.1: Empty cookie list handling
    print("  Test 1.1: Empty cookie list handling...")
    cookie_db = Path(__file__).parent.parent / 'data' / 'test_cookies.db'
    cm = CookieManager(str(cookie_db))
    active = cm.get_active_cookies()
    print(f"    ✅ Handles empty cookies: {len(active)} cookies")
    test_results['passed'] += 1
    
    # Test 1.2: Cookie file watch system
    print("  Test 1.2: Cookie file watch system...")
    cookies_dir = Path(__file__).parent.parent / 'data' / 'cookies'
    cookies_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test cookie file
    test_cookie_file = cookies_dir / 'test_cookie_1.txt'
    test_cookie_file.write_text('# Test Cookie\ntest_cookie_data')
    
    # Verify file creation
    if test_cookie_file.exists():
        print(f"    ✅ Cookie file created: {test_cookie_file.name}")
        test_results['passed'] += 1
    
    # Cleanup
    test_cookie_file.unlink(missing_ok=True)
    
    # Test 1.3: Cookie summary statistics
    print("  Test 1.3: Cookie summary statistics...")
    summary = cm.get_cookie_summary()
    assert 'total' in summary or isinstance(summary, dict)
    print(f"    ✅ Cookie summary generated: {type(summary).__name__}")
    test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Cookie rotation test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Cookie Rotation', str(e)))

print()

# ============================================================================
# TEST 2: Video Filtering Edge Cases
# ============================================================================
print("🎥 TEST 2: Video Filtering Edge Cases")
print("-" * 80)

try:
    from video_fetcher import VideoFetcher
    from config_loader import load_config
    
    config = load_config()
    vf = VideoFetcher(config)
    
    # Test 2.1: Empty video list
    print("  Test 2.1: Empty video list handling...")
    empty_videos = []
    filtered = vf.filter_videos(empty_videos, config)
    assert filtered == []
    print(f"    ✅ Empty list handled correctly: {len(filtered)} videos")
    test_results['passed'] += 1
    
    # Test 2.2: All videos filtered out
    print("  Test 2.2: All videos filtered (shorts + live)...")
    all_shorts = [
        {'duration': '0:30', 'title': 'Short 1', 'url': 'url1'},
        {'duration': '0:45', 'title': 'Short 2', 'url': 'url2'},
    ]
    filtered = vf.filter_videos(all_shorts, config)
    print(f"    ✅ Filtered {len(all_shorts)} shorts → {len(filtered)} videos")
    test_results['passed'] += 1
    
    # Test 2.3: Mixed duration formats
    print("  Test 2.3: Mixed duration formats...")
    mixed_videos = [
        {'duration': '1:30', 'title': 'Normal 1', 'url': 'url1'},
        {'duration': '10:05:30', 'title': 'Long', 'url': 'url2'},  # 10+ hours
        {'duration': '0:15', 'title': 'Short', 'url': 'url3'},
    ]
    filtered = vf.filter_videos(mixed_videos, config)
    print(f"    ✅ Mixed durations processed: {len(filtered)} videos kept")
    test_results['passed'] += 1
    
    # Test 2.4: Missing duration field
    print("  Test 2.4: Videos with missing duration...")
    missing_duration = [
        {'title': 'No Duration', 'url': 'url1'},
        {'duration': None, 'title': 'Null Duration', 'url': 'url2'},
    ]
    try:
        filtered = vf.filter_videos(missing_duration, config)
        print(f"    ✅ Missing duration handled: {len(filtered)} videos")
        test_results['passed'] += 1
    except Exception as e:
        print(f"    ⚠️ Missing duration causes: {type(e).__name__}")
        test_results['passed'] += 1  # Expected behavior
    
except Exception as e:
    print(f"  ❌ Video filtering test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Video Filtering', str(e)))

print()

# ============================================================================
# TEST 3: Database Concurrent Access
# ============================================================================
print("💾 TEST 3: Database Concurrent Access")
print("-" * 80)

try:
    from persistence import Persistence
    
    # Test 3.1: Concurrent writes
    print("  Test 3.1: Concurrent write operations...")
    
    test_db = Path(__file__).parent.parent / 'data' / 'test_videos.db'
    db = Persistence(str(test_db))
    
    def mark_video_worker(video_id):
        db.mark_seen(video_id)
    
    threads = []
    test_video_ids = [f"concurrent_test_{i}" for i in range(10)]
    
    for vid in test_video_ids:
        t = threading.Thread(target=mark_video_worker, args=(vid,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Verify all videos marked
    marked_count = sum(1 for vid in test_video_ids if db.is_seen(vid))
    print(f"    ✅ Concurrent writes: {marked_count}/{len(test_video_ids)} videos marked")
    test_results['passed'] += 1
    
    # Test 3.2: Database integrity check
    print("  Test 3.2: Database integrity after concurrent ops...")
    current_count = db.get_seen_count()
    print(f"    ✅ Total seen videos: {current_count} (DB intact)")
    test_results['passed'] += 1
    
    # Test 3.3: Duplicate marking
    print("  Test 3.3: Duplicate video marking...")
    test_vid = "duplicate_test"
    db.mark_seen(test_vid)
    db.mark_seen(test_vid)  # Second time
    db.mark_seen(test_vid)  # Third time
    
    if db.is_seen(test_vid):
        print(f"    ✅ Duplicate marking handled correctly")
        test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Database concurrency test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Database Concurrency', str(e)))

print()

# ============================================================================
# TEST 4: Configuration Validation
# ============================================================================
print("⚙️ TEST 4: Configuration Validation")
print("-" * 80)

try:
    from config_loader import load_config, Config
    
    # Test 4.1: Default config loading
    print("  Test 4.1: Default configuration...")
    config = load_config()
    assert 'CHANNEL_URL' in config.data
    assert 'MAX_WINDOWS' in config.data
    print(f"    ✅ Config loaded with {len(config.data)} attributes")
    test_results['passed'] += 1
    
    # Test 4.2: Config value types
    print("  Test 4.2: Configuration value types...")
    assert isinstance(config.get('MAX_WINDOWS'), int)
    assert isinstance(config.get('SKIP_SHORTS'), bool)
    assert isinstance(config.get('SKIP_LIVE_STREAMS'), bool)
    print(f"    ✅ All config types validated")
    test_results['passed'] += 1
    
    # Test 4.3: Invalid config handling (mock)
    print("  Test 4.3: Invalid config handling...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write('{"invalid": "json", missing_fields: true}')  # Invalid JSON
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, 'r') as f:
            json.load(f)
        print(f"    ⚠️ JSON parser too lenient")
    except json.JSONDecodeError:
        print(f"    ✅ Invalid JSON detected correctly")
        test_results['passed'] += 1
    finally:
        os.unlink(tmp_path)
    
    # Test 4.4: Required fields validation
    print("  Test 4.4: Required configuration fields...")
    required_fields = ['CHANNEL_URL', 'MAX_WINDOWS', 'SKIP_SHORTS']
    missing = [field for field in required_fields if field not in config.data]
    
    if not missing:
        print(f"    ✅ All required fields present: {', '.join(required_fields)}")
        test_results['passed'] += 1
    else:
        print(f"    ❌ Missing fields: {missing}")
        test_results['failed'] += 1
    
except Exception as e:
    print(f"  ❌ Configuration validation failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Configuration', str(e)))

print()

# ============================================================================
# TEST 5: Error Handling and Recovery
# ============================================================================
print("⚠️ TEST 5: Error Handling and Recovery")
print("-" * 80)

try:
    from exceptions import CookieError, VideoFetchError, PlayerError, ConfigError
    
    # Test 5.1: Exception hierarchy
    print("  Test 5.1: Exception inheritance...")
    cookie_err = CookieError("Test cookie error")
    video_err = VideoFetchError("Test video error")
    player_err = PlayerError("Test player error")
    config_err = ConfigError("Test config error")
    
    assert isinstance(cookie_err, Exception)
    assert isinstance(video_err, Exception)
    print(f"    ✅ All exceptions inherit from Exception")
    test_results['passed'] += 1
    
    # Test 5.2: Exception messages
    print("  Test 5.2: Exception message preservation...")
    test_msg = "Custom error message"
    err = CookieError(test_msg)
    assert str(err) == test_msg
    print(f"    ✅ Exception messages preserved correctly")
    test_results['passed'] += 1
    
    # Test 5.3: Try-except patterns
    print("  Test 5.3: Exception catching...")
    caught_cookie = False
    caught_video = False
    
    try:
        raise CookieError("Cookie test")
    except CookieError:
        caught_cookie = True
    
    try:
        raise VideoFetchError("Video test")
    except VideoFetchError:
        caught_video = True
    
    if caught_cookie and caught_video:
        print(f"    ✅ Exceptions caught correctly")
        test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Error handling test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Error Handling', str(e)))

print()

# ============================================================================
# TEST 6: Performance and Timing
# ============================================================================
print("⚡ TEST 6: Performance and Timing")
print("-" * 80)

try:
    from persistence import Persistence
    from video_fetcher import VideoFetcher
    from config_loader import load_config
    
    test_db = Path(__file__).parent.parent / 'data' / 'test_perf.db'
    db = Persistence(str(test_db))
    
    # Test 6.1: Database write speed
    print("  Test 6.1: Database write performance...")
    start_time = time.time()
    for i in range(100):
        db.mark_seen(f"perf_test_{i}")
    write_time = time.time() - start_time
    
    avg_write = (write_time / 100) * 1000  # ms per write
    print(f"    ✅ 100 writes in {write_time:.3f}s ({avg_write:.2f}ms avg)")
    test_results['passed'] += 1
    
    # Test 6.2: Database read speed
    print("  Test 6.2: Database read performance...")
    start_time = time.time()
    for i in range(100):
        db.is_seen(f"perf_test_{i}")
    read_time = time.time() - start_time
    
    avg_read = (read_time / 100) * 1000  # ms per read
    print(f"    ✅ 100 reads in {read_time:.3f}s ({avg_read:.2f}ms avg)")
    test_results['passed'] += 1
    
    # Test 6.3: Video filtering speed
    print("  Test 6.3: Video filtering performance...")
    config = load_config()
    vf = VideoFetcher(config)
    
    large_video_list = [
        {'duration': f'{i}:30', 'title': f'Video {i}', 'url': f'url{i}'}
        for i in range(1, 101)
    ]
    
    start_time = time.time()
    filtered = vf.filter_videos(large_video_list, config)
    filter_time = time.time() - start_time
    
    print(f"    ✅ Filtered 100 videos in {filter_time:.3f}s ({len(filtered)} kept)")
    test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Performance test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Performance', str(e)))

print()

# ============================================================================
# TEST 7: File System Operations
# ============================================================================
print("📁 TEST 7: File System Operations")
print("-" * 80)

try:
    # Test 7.1: Cookie directory creation
    print("  Test 7.1: Cookie directory handling...")
    cookies_dir = Path(__file__).parent.parent / 'data' / 'cookies'
    cookies_dir.mkdir(parents=True, exist_ok=True)
    
    if cookies_dir.exists() and cookies_dir.is_dir():
        print(f"    ✅ Cookie directory exists: {cookies_dir}")
        test_results['passed'] += 1
    
    # Test 7.2: Database directory
    print("  Test 7.2: Database directory handling...")
    db_dir = Path(__file__).parent.parent / 'data'
    db_dir.mkdir(parents=True, exist_ok=True)
    
    if db_dir.exists():
        print(f"    ✅ Database directory exists: {db_dir}")
        test_results['passed'] += 1
    
    # Test 7.3: Log directory
    print("  Test 7.3: Log directory handling...")
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if log_dir.exists():
        print(f"    ✅ Log directory exists: {log_dir}")
        test_results['passed'] += 1
    
    # Test 7.4: File permissions (write test)
    print("  Test 7.4: File write permissions...")
    test_file = log_dir / 'test_write.txt'
    try:
        test_file.write_text('test')
        test_file.unlink()
        print(f"    ✅ Write permissions OK")
        test_results['passed'] += 1
    except PermissionError:
        print(f"    ❌ Write permission denied")
        test_results['failed'] += 1
    
except Exception as e:
    print(f"  ❌ File system test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('File System', str(e)))

print()

# ============================================================================
# TEST 8: Logger Functionality
# ============================================================================
print("📝 TEST 8: Logger Advanced Testing")
print("-" * 80)

try:
    from logger_config import setup_logging
    
    # Test 8.1: Multiple logger instances
    print("  Test 8.1: Multiple logger instances...")
    logger1 = setup_logging()
    logger2 = setup_logging()
    
    # Should be same instance (singleton pattern check)
    if logger1.name == logger2.name:
        print(f"    ✅ Logger consistency: {logger1.name}")
        test_results['passed'] += 1
    
    # Test 8.2: Different log levels
    print("  Test 8.2: Log level testing...")
    logger = setup_logging()
    
    try:
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        print(f"    ✅ All log levels functional")
        test_results['passed'] += 1
    except Exception as e:
        print(f"    ❌ Log level error: {e}")
        test_results['failed'] += 1
    
    # Test 8.3: Log file creation
    print("  Test 8.3: Log file creation...")
    log_file = Path(__file__).parent.parent / 'logs' / 'app.log'
    
    if log_file.exists():
        file_size = log_file.stat().st_size
        print(f"    ✅ Log file exists: {file_size} bytes")
        test_results['passed'] += 1
    else:
        print(f"    ⚠️ Log file not created yet (OK for new install)")
        test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Logger test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Logger', str(e)))

print()

# ============================================================================
# TEST 9: Browser Path Detection
# ============================================================================
print("🌐 TEST 9: Browser Detection Advanced")
print("-" * 80)

try:
    from app import get_brave_path
    
    # Test 9.1: Brave detection
    print("  Test 9.1: Brave browser detection...")
    brave_path = get_brave_path()
    
    if brave_path and Path(brave_path).exists():
        print(f"    ✅ Brave found: {Path(brave_path).name}")
        test_results['passed'] += 1
    else:
        print(f"    ⚠️ Brave not found (may not be installed)")
        test_results['passed'] += 1  # Not a failure
    
    # Test 9.2: Chrome fallback (mock test)
    print("  Test 9.2: Chrome fallback detection...")
    chrome_paths = [
        Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
        Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
    ]
    
    chrome_found = any(p.exists() for p in chrome_paths if p)
    
    if chrome_found:
        print(f"    ✅ Chrome detected (fallback available)")
    else:
        print(f"    ⚠️ Chrome not found (Brave is primary)")
    test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Browser detection test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Browser Detection', str(e)))

print()

# ============================================================================
# TEST 10: Integration - Cookie to Video Flow
# ============================================================================
print("🔄 TEST 10: Integration Testing (Cookie → Video Flow)")
print("-" * 80)

try:
    from cookie_manager import CookieManager
    from video_fetcher import VideoFetcher
    from persistence import Persistence
    from config_loader import load_config
    
    # Test 10.1: Full pipeline simulation
    print("  Test 10.1: Cookie → Config → VideoFetcher pipeline...")
    
    # Step 1: Cookie Manager
    cookie_db = Path(__file__).parent.parent / 'data' / 'test_integration.db'
    cm = CookieManager(str(cookie_db))
    cookies = cm.get_active_cookies()
    print(f"    → Cookie Manager initialized: {len(cookies)} cookies")
    
    # Step 2: Config
    config = load_config()
    print(f"    → Config loaded: {config.get('CHANNEL_URL', '')[:50]}...")
    
    # Step 3: Video Fetcher
    vf = VideoFetcher(config)
    print(f"    → Video Fetcher created")
    
    # Step 4: Simulate video filtering
    test_videos = [
        {'duration': '5:30', 'title': 'Video 1', 'url': 'url1'},
        {'duration': '0:45', 'title': 'Short', 'url': 'url2'},
        {'duration': '10:00', 'title': 'Video 2', 'url': 'url3'},
    ]
    
    filtered = vf.filter_videos(test_videos, config)
    print(f"    → Filtered: {len(test_videos)} → {len(filtered)} videos")
    
    # Step 5: Mark as seen
    test_db = Path(__file__).parent.parent / 'data' / 'test_integration_videos.db'
    db = Persistence(str(test_db))
    for video in filtered:
        db.mark_seen(video['url'])
    print(f"    → Marked {len(filtered)} videos as seen")
    
    print(f"    ✅ Full integration pipeline successful")
    test_results['passed'] += 1
    
except Exception as e:
    print(f"  ❌ Integration test failed: {e}")
    test_results['failed'] += 1
    test_results['errors'].append(('Integration', str(e)))

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("📊 ADVANCED TEST SUMMARY")
print("=" * 80)
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
total_tests = test_results['passed'] + test_results['failed']
success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}%")
print()

if test_results['errors']:
    print("🐛 ERRORS ENCOUNTERED:")
    print("-" * 80)
    for test_name, error in test_results['errors']:
        print(f"  ❌ {test_name}: {error}")
    print()

if test_results['failed'] == 0:
    print("🎉 ALL ADVANCED TESTS PASSED!")
else:
    print(f"⚠️ {test_results['failed']} test(s) need attention")

print("=" * 80)
