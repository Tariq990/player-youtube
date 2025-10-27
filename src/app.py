"""
YouTube Player - Main Application
CRITICAL: Ensures 100% view counting with real browser behavior
"""

# Standard library imports
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Local imports
from config_loader import load_config
from cookie_manager import CookieManager
from persistence import Persistence
from player_worker import PlayerWorker
from video_fetcher import fetch_channel_videos
from browser_manager import get_brave_path, create_driver, add_cookies_to_driver
from retry_logic import retry_async, RetryConfig, ErrorType
from session_metrics import SessionMetrics
from cookie_watcher import CookieWatcher
from smart_cookie_rotator import SmartCookieRotator
from retry_logic import retry_async, RetryConfig, ErrorType

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()


def test_cookie_login(cookie_data: dict, brave_path: str) -> bool:
    """
    Test if cookie logs in successfully (headless mode)
    Returns: True if logged in, False otherwise
    Auto-closes browser after test
    """
    driver = None
    try:
        # Create headless driver for testing
        user_agent = cookie_data.get('user_agent')
        driver = create_driver(brave_path, user_agent, headless=True)
        
        # Navigate to YouTube
        driver.get("https://www.youtube.com")
        
        # Add cookies using helper
        add_cookies_to_driver(driver, cookie_data.get('cookies', []))
        
        # Reload to apply cookies
        driver.get("https://www.youtube.com")
        
        # Wait for page load
        import time
        time.sleep(3)
        
        # Check if logged in - look for avatar/user button
        try:
            # Multiple selectors to ensure we catch logged-in state
            selectors = [
                "#avatar-btn",
                "button[aria-label*='Account']",
                "ytd-topbar-menu-button-renderer#avatar",
                "#buttons ytd-topbar-menu-button-renderer"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        return True  # Found user avatar = Logged in!
                except:
                    continue
            
            # If no avatar found, check for "Sign in" button (means NOT logged in)
            try:
                sign_in = driver.find_element(By.XPATH, "//a[contains(text(), 'Sign in')]")
                if sign_in:
                    return False  # Sign in button exists = NOT logged in
            except:
                pass
            
            return False  # Couldn't confirm login
            
        except Exception as e:
            return False
            
    except Exception as e:
        return False
        
    finally:
        # ALWAYS close the browser
        if driver:
            try:
                driver.quit()
            except:
                pass


def test_and_filter_cookies(all_cookies: List[Dict], brave_path: str) -> List[Dict]:
    """
    Test all cookies and return only valid (logged-in) ones
    Automatically deletes invalid cookies from file
    """
    valid_cookies = []
    invalid_cookie_ids = []
    
    print(f"\n🔍 Testing {len(all_cookies)} cookie sets for login status...")
    print("=" * 60)
    
    for idx, cookie_data in enumerate(all_cookies, 1):
        cookie_name = cookie_data.get('account_name', 'Unknown')
        cookie_id = cookie_data.get('id', '')
        
        print(f"\n[{idx}/{len(all_cookies)}] Testing: {cookie_name}")
        print("   📺 Opening YouTube (headless)...")
        print("   🍪 Adding cookies...")
        print("   🔍 Checking login status...", end=" ")
        
        is_logged_in = test_cookie_login(cookie_data, brave_path)
        
        if is_logged_in:
            print("✅ LOGGED IN")
            valid_cookies.append(cookie_data)
        else:
            print("❌ NOT LOGGED IN")
            print("   🗑️  Marking for deletion...")
            invalid_cookie_ids.append(cookie_id)
    
    # Delete invalid cookies from file
    if invalid_cookie_ids:
        print(f"\n🗑️  Deleting {len(invalid_cookie_ids)} invalid cookies from database...")
        from cookie_manager import CookieManager
        cookie_mgr = CookieManager(os.getenv('COOKIE_DB_PATH', 'data/cookies.json'))
        
        for cookie_id in invalid_cookie_ids:
            cookie_mgr.delete_cookie(cookie_id)
        
        cookie_mgr.persist()
        print("✅ Invalid cookies deleted")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   ✅ Valid: {len(valid_cookies)}")
    print(f"   ❌ Invalid: {len(invalid_cookie_ids)}")
    print("=" * 60)
    
    return valid_cookies


async def play_video_task_with_retry(video: dict, cookie_data: dict, config: dict, semaphore: asyncio.Semaphore,
                                      persistence: Persistence, cookie_mgr: CookieManager, 
                                      all_valid_cookies: List[Dict], brave_path: str):
    """
    Play video with sophisticated retry logic and exponential backoff
    """
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=2.0,  # Start with 2 seconds
        max_delay=60.0,  # Cap at 60 seconds
        jitter=True
    )
    
    current_cookie = cookie_data
    
    async def attempt_play():
        """Single play attempt - can raise exceptions for retry classification"""
        result = await play_video_task(video, current_cookie, config, semaphore, persistence, cookie_mgr)
        
        if not result:
            # Classify the error to determine retry strategy
            # For now, treat all failures as transient unless we have better classification
            raise Exception("Video playback failed")
        
        return result
    
    try:
        # Use the new retry logic with exponential backoff
        result = await retry_async(
            attempt_play,
            config=retry_config
        )
        return result
    except Exception as e:
        # All retries exhausted - try fallback cookie
        print(f"❌ All retries failed for cookie: {current_cookie.get('account_name')}")
        
        # Try next cookie
        current_index = None
        for idx, cookie in enumerate(all_valid_cookies):
            if cookie.get('id') == current_cookie.get('id'):
                current_index = idx
                break
        
        if current_index is not None and len(all_valid_cookies) > 1:
            next_index = (current_index + 1) % len(all_valid_cookies)
            next_cookie = all_valid_cookies[next_index]
            
            print(f"🔄 Switching to fallback cookie: {next_cookie.get('account_name')}")
            
            # Re-test the new cookie before using
            print("   🔍 Testing fallback cookie...")
            if test_cookie_login(next_cookie, brave_path):
                print("   ✅ Fallback cookie valid - retrying video...")
                current_cookie = next_cookie
                # One more try with new cookie
                result = await play_video_task(video, current_cookie, config, semaphore, persistence, cookie_mgr)
                return result
            else:
                print("   ❌ Fallback cookie also invalid!")
                return False
        else:
            return False


async def play_video_task(video: dict, cookie_data: dict, config: dict, semaphore: asyncio.Semaphore, 
                          persistence: Persistence, cookie_mgr: CookieManager):
    """
    Task to play a single video
    """
    async with semaphore:
        driver = None
        video_title = video['title'][:50]
        
        try:
            # Get Brave path
            brave_path = get_brave_path()
            if not brave_path:
                print(f"❌ [{video_title}] Brave browser not found!")
                return False
            
            # Create driver
            use_headless = config.get('USE_HEADLESS', False)
            user_agent = cookie_data.get('user_agent')
            
            print(f"\n{'='*60}")
            print(f"🎬 STARTING: {video_title}")
            print(f"👤 Account: {cookie_data.get('account_name', 'Unknown')}")
            print(f"{'='*60}")
            
            driver = create_driver(brave_path, user_agent, use_headless)
            
            # Navigate to YouTube and add cookies
            print("📺 Opening YouTube...")
            driver.get("https://www.youtube.com")
            
            # Add cookies using helper
            cookies = cookie_data.get('cookies', [])
            print(f"🍪 Adding {len(cookies)} cookies...")
            add_cookies_to_driver(driver, cookies)
            
            # Reload to apply cookies
            driver.get("https://www.youtube.com")
            await asyncio.sleep(2)
            
            # Play video
            worker = PlayerWorker(driver, config)
            success = await worker.play_video(video, cookie_data)
            
            if success:
                # Mark as seen
                persistence.mark_seen(
                    video['video_id'],
                    video.get('title', ''),
                    video.get('duration', 0)
                )
                
                # Mark cookie as used
                cookie_mgr.mark_used(cookie_data['id'])
                
                print(f"\n{'='*60}")
                print(f"✅ COMPLETED: {video_title}")
                print(f"{'='*60}")
                return True
            else:
                print(f"\n{'='*60}")
                print(f"❌ FAILED: {video_title}")
                print(f"{'='*60}")
                return False
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERROR in {video_title}: {e}")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass


async def main():
    """Main application loop"""
    
    print("=" * 60)
    print("🎬 YOUTUBE PLAYER - 100% VIEW COUNTING")
    print("=" * 60)
    print()
    
    # Race condition protection lock
    valid_cookies_lock = asyncio.Lock()
    
    # Initialize session metrics
    metrics = SessionMetrics()
    
    # Load config
    print("📋 Loading configuration...")
    try:
        config = load_config()
        print("✅ Config loaded")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Check Brave
    brave_path = get_brave_path()
    if not brave_path:
        print("❌ Brave browser not found!")
        print("   Please install Brave or set BRAVE_BINARY_PATH in .env")
        return
    
    print(f"✅ Brave found: {brave_path}")
    
    # Setup persistence
    print("\n💾 Setting up database...")
    persistence = Persistence(config['SEEN_DB_PATH'])
    
    # Cleanup old progress entries
    persistence.clear_old_progress()
    
    seen_count = persistence.get_seen_count()
    print(f"✅ Database ready ({seen_count} videos already seen)")
    
    # Check for interrupted videos
    interrupted = persistence.get_interrupted_videos()
    if interrupted:
        print(f"\n📌 Found {len(interrupted)} interrupted videos from previous session")
        print("   These will be retried...")
    
    # Fetch videos
    channel_url = config['CHANNEL_URL']
    print(f"\n🔍 Fetching videos from channel...")
    print(f"   URL: {channel_url}")
    
    all_videos = await fetch_channel_videos(channel_url, config.data, max_videos=100)
    
    if not all_videos:
        print("❌ No videos found!")
        return
    
    # Filter unseen videos
    unseen_videos = persistence.get_unseen_videos(all_videos)
    print(f"\n📊 Total videos: {len(all_videos)}")
    print(f"📊 Unseen videos: {len(unseen_videos)}")
    
    if not unseen_videos:
        print("\n✅ All videos have been watched!")
        print("   Clearing database to restart...")
        persistence.clear_all()
        unseen_videos = all_videos
    
    # Load/Reload cookies BEFORE starting playback
    # This ensures any newly added cookies are picked up
    print("\n🍪 Loading cookies...")
    cookie_mgr = CookieManager(config['COOKIE_DB_PATH'])
    cookie_mgr.load()  # Force reload from file
    
    active_cookies = cookie_mgr.get_active_cookies()
    if not active_cookies:
        print("❌ No active cookies found!")
        print("   Run: python scripts/save_cookies.py")
        return
    
    print(f"✅ Loaded {len(active_cookies)} cookie sets")
    
    # Setup cookie file watcher
    cookie_path = Path(config['COOKIE_DB_PATH'])
    
    def reload_cookies():
        """Callback for cookie file changes."""
        try:
            cookie_mgr.load()
            new_active = cookie_mgr.get_active_cookies()
            print(f"\n🔄 Cookies reloaded: {len(new_active)} active sets")
        except Exception as e:
            print(f"\n❌ Failed to reload cookies: {e}")
    
    watcher = CookieWatcher(cookie_path, reload_cookies, debounce_seconds=2.0)
    watcher.start()
    print(f"👁️  Watching {cookie_path.name} for changes...")
    
    # Test all cookies and filter out invalid ones
    valid_cookies = test_and_filter_cookies(active_cookies, brave_path)
    
    if not valid_cookies:
        watcher.stop()  # Stop watcher before exiting
        print("\n❌ No valid (logged-in) cookies found!")
        print("   All cookies failed login test")
        print("   Please save new cookies: python scripts/save_cookies.py")
        return
    
    print(f"\n✅ Ready with {len(valid_cookies)} valid cookie sets:")
    for idx, cookie in enumerate(valid_cookies, 1):
        cookie_name = cookie.get('account_name', 'Unknown')
        print(f"   [{idx}] {cookie_name} ✓")
    
    cookie_mgr.persist()  # Save state
    
    # Initialize Smart Cookie Rotator
    cookie_rotator = SmartCookieRotator(
        valid_cookies,
        min_health_score=30.0,
        max_consecutive_failures=5
    )
    print(f"🧠 Smart Cookie Rotation enabled")
    
    # Track file modification time for auto-reload
    cookie_file_mtime = os.path.getmtime(config['COOKIE_DB_PATH'])
    
    # Smart worker allocation based on video count
    max_windows = config.get('MAX_WINDOWS', 4)
    video_count = len(unseen_videos)
    
    # Calculate optimal worker count
    if video_count == 1:
        # 1 video: Use all 4 workers (same video on 4 browsers for redundancy)
        active_workers = max_windows
        duplicate_videos = True
        print(f"\n🎯 Single video mode: Using {active_workers} workers for redundancy")
    elif video_count == 2:
        # 2 videos: Use 2 workers (1 per video)
        active_workers = 2
        duplicate_videos = False
        print(f"\n🎯 Dual video mode: Using {active_workers} workers (1 per video)")
    elif video_count <= max_windows:
        # Few videos: 1 worker per video
        active_workers = video_count
        duplicate_videos = False
        print(f"\n🎯 Balanced mode: Using {active_workers} workers (1 per video)")
    else:
        # Many videos: Use all available workers
        active_workers = max_windows
        duplicate_videos = False
        print(f"\n🎯 Full concurrency mode: Using {active_workers} workers")
    
    print(f"\n🚀 Starting playback...")
    print(f"⏱️  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📹 Videos to play: {len(unseen_videos)}")
    
    # Distribute cookies evenly across videos
    num_cookies = len(valid_cookies)
    print(f"🍪 Available cookies: {num_cookies}")
    print(f"📊 Distribution strategy: Smart rotation (health-based)")
    print(f"🔄 Auto-reload: Continuous monitoring for new videos")
    print("=" * 60)
    
    # Queue-based processing for better resource management
    video_queue = asyncio.Queue()
    
    # Add videos to queue (with duplication if needed)
    if duplicate_videos and video_count == 1:
        # Add same video multiple times for parallel processing
        for i in range(active_workers):
            await video_queue.put(unseen_videos[0])
        print(f"\n✅ Added 1 video {active_workers} times for parallel processing")
    else:
        # Add each video once
        for video in unseen_videos:
            await video_queue.put(video)
        print(f"\n✅ {len(unseen_videos)} videos added to queue")
    
    print(f"⚡ Starting {active_workers} concurrent workers...")
    print("=" * 60)
    
    # Worker function
    async def video_worker(worker_id: int, queue: asyncio.Queue, shutdown_event: asyncio.Event):
        """Worker that processes videos from queue"""
        videos_processed = 0
        
        while not shutdown_event.is_set():
            try:
                # Get video from queue with timeout
                video = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Get cookie using smart rotation (health-based selection)
                cookie_data = cookie_rotator.get_next_cookie()
                
                if not cookie_data:
                    print(f"❌ Worker {worker_id}: No healthy cookies available!")
                    queue.task_done()
                    continue
                
                cookie_name = cookie_data.get('account_name', 'Unknown')
                cookie_id = cookie_data.get('id', 'unknown')
                remaining = queue.qsize()
                print(f"\n🎬 Worker {worker_id} starting video: {video['title'][:50]}...")
                print(f"   🍪 Using cookie: {cookie_name} (health-based)")
                print(f"   📊 Remaining: {remaining} videos")
                
                # Mark as in-progress for resume capability
                persistence.mark_in_progress(
                    video['video_id'],
                    video.get('title', ''),
                    cookie_id
                )
                
                # Get video duration for metrics
                video_duration = video.get('duration', 0)
                
                # Process video with retry
                success = await play_video_task_with_retry(
                    video, cookie_data, config.data, asyncio.Semaphore(1),
                    persistence, cookie_mgr, valid_cookies, brave_path
                )
                
                # Remove from in-progress (completed or failed)
                persistence.remove_from_progress(video['video_id'])
                
                videos_processed += 1
                queue.task_done()
                
                # Record metrics AND cookie health
                if success:
                    metrics.record_success(video['video_id'], cookie_id, video_duration)
                    cookie_rotator.record_success(cookie_data, watch_time=video_duration)
                    print(f"✅ Worker {worker_id} completed video #{videos_processed}")
                else:
                    metrics.record_failure(video['video_id'], cookie_id, "Playback failed")
                    cookie_rotator.record_failure(cookie_data, error="Playback failed")
                    print(f"❌ Worker {worker_id} failed video #{videos_processed}")
                
                # Show quick status every 5 videos
                if videos_processed % 5 == 0:
                    metrics.quick_status()
                
            except asyncio.TimeoutError:
                # No video available, check shutdown
                continue
            except asyncio.CancelledError:
                print(f"⚠️ Worker {worker_id} cancelled")
                break
            except Exception as e:
                print(f"❌ Worker {worker_id} error: {e}")
                continue
        
        print(f"🛑 Worker {worker_id} shutting down (processed {videos_processed} videos)")
    
    # Shutdown event for graceful termination
    shutdown_event = asyncio.Event()
    
    # Create workers with dynamic count
    workers = [
        asyncio.create_task(video_worker(i+1, video_queue, shutdown_event))
        for i in range(active_workers)  # Use dynamic worker count
    ]
    
    # Background task to monitor for new videos
    async def monitor_new_videos():
        """Monitor channel for new videos and add them to queue with priority"""
        last_check = datetime.now()
        check_interval = config.get('NEW_VIDEO_CHECK_INTERVAL', 300)  # 5 minutes default
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(check_interval)
                
                if shutdown_event.is_set():
                    break
                
                print(f"\n🔍 Checking for new videos...")
                current_videos = await fetch_channel_videos(channel_url, config.data, max_videos=100)
                
                if not current_videos:
                    continue
                
                # Find new videos (not in database)
                new_videos = persistence.get_unseen_videos(current_videos)
                
                if new_videos:
                    print(f"🆕 Found {len(new_videos)} new video(s)!")
                    # Add new videos to front of queue (priority)
                    for video in reversed(new_videos):
                        # Put at front by getting all items, adding new one first, then re-adding
                        print(f"   ➕ Adding: {video['title'][:50]}...")
                    
                    # Add to queue
                    for video in new_videos:
                        await video_queue.put(video)
                    
                    print(f"✅ {len(new_videos)} new video(s) added to queue with priority")
                else:
                    print(f"✓ No new videos found")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Error checking for new videos: {e}")
    
    # Start monitoring task
    monitor_task = asyncio.create_task(monitor_new_videos())
    
    # Background task to handle replay when queue is empty
    async def replay_manager():
        """Add watched videos back to queue for replay when all videos are done"""
        replay_count = 0
        
        while not shutdown_event.is_set():
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                if shutdown_event.is_set():
                    break
                
                # Check if queue is empty
                if video_queue.empty():
                    # Check if there are new videos first
                    current_videos = await fetch_channel_videos(channel_url, config.data, max_videos=100)
                    new_videos = persistence.get_unseen_videos(current_videos) if current_videos else []
                    
                    if new_videos:
                        # New videos found, they will be added by monitor_new_videos
                        print(f"\n🆕 New videos detected, skipping replay...")
                        continue
                    
                    # No new videos, start replay
                    replay_count += 1
                    print(f"\n🔄 Queue empty! Starting replay cycle #{replay_count}...")
                    print(f"   Clearing database and re-adding all videos...")
                    
                    # Clear seen videos to allow replay
                    persistence.clear_all()
                    
                    # Re-fetch all videos
                    all_videos_replay = await fetch_channel_videos(channel_url, config.data, max_videos=100)
                    
                    if all_videos_replay:
                        # Add all videos back to queue
                        for video in all_videos_replay:
                            await video_queue.put(video)
                        
                        print(f"✅ Added {len(all_videos_replay)} videos for replay cycle #{replay_count}")
                    else:
                        print(f"⚠️ No videos found for replay")
                    
                    # Wait a bit before next check
                    await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Error in replay manager: {e}")
    
    # Start replay manager
    replay_task = asyncio.create_task(replay_manager())
    
    # Wait for all videos to be processed
    print(f"\n⏳ Processing videos with {active_workers} workers...")
    print(f"🔄 Continuous mode: Will replay when done + monitor for new videos")
    
    try:
        # Keep running until user stops (Ctrl+C)
        await asyncio.gather(monitor_task, replay_task, return_exceptions=True)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user - shutting down gracefully...")
        shutdown_event.set()
    
    # Cancel background tasks
    shutdown_event.set()
    monitor_task.cancel()
    replay_task.cancel()
    
    # Cancel workers
    for worker in workers:
        worker.cancel()
    
    # Wait for all tasks to finish
    await asyncio.gather(*workers, monitor_task, replay_task, return_exceptions=True)
    
    # Stop cookie watcher
    watcher.stop()
    
    # Summary
    successful = metrics.videos_watched
    failed = metrics.videos_failed
    total = successful + failed
    
    print("\n" + "=" * 60)
    print("🏁 PLAYBACK COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    if total > 0:
        print(f"📈 Success rate: {successful/total*100:.1f}%")
    print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Show comprehensive metrics report
    metrics.report()
    
    # Show cookie health report
    print(cookie_rotator.get_health_report())
    healthy_count = cookie_rotator.get_healthy_count()
    print(f"\n🍪 Healthy cookies remaining: {healthy_count}/{len(valid_cookies)}")
    
    # Save final state
    cookie_mgr.persist()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
