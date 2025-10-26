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

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()


def get_brave_path():
    """Get Brave browser executable path"""
    env_path = os.getenv('BRAVE_BINARY_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    brave_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    
    for path in brave_paths:
        if os.path.exists(path):
            return path
    return None


def create_driver(brave_path: str, user_agent: Optional[str] = None, headless: bool = False):
    """Create a Brave browser driver"""
    chrome_options = Options()
    chrome_options.binary_location = brave_path
    
    # Headless or visible
    if headless:
        chrome_options.add_argument('--headless=new')
    else:
        chrome_options.add_argument('--start-maximized')
    
    # Basic options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Set user agent if provided
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Anti-detection (CRITICAL for view counting)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Create driver - try system ChromeDriver first, then webdriver-manager
    try:
        # Try system ChromeDriver
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        # Fallback to webdriver-manager
        try:
            service = Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Last resort - just use default
            driver = webdriver.Chrome(options=chrome_options)
    
    # Hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


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
        
        # Add cookies
        cookies = cookie_data.get('cookies', [])
        for cookie in cookies:
            try:
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', '.youtube.com'),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                }
                
                if 'expiry' in cookie:
                    cookie_dict['expiry'] = int(cookie['expiry'])
                elif 'expirationDate' in cookie:
                    cookie_dict['expiry'] = int(cookie['expirationDate'])
                
                driver.add_cookie(cookie_dict)
            except:
                pass
        
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
    Play video with retry logic and cookie fallback
    """
    max_retries = 2
    retry_delay = 30  # seconds
    
    current_cookie = cookie_data
    
    for attempt in range(max_retries + 1):
        result = await play_video_task(video, current_cookie, config, semaphore, persistence, cookie_mgr)
        
        if result:
            return True  # Success!
        
        # Failed - determine if we should retry
        if attempt < max_retries:
            print(f"⏳ Retry {attempt + 1}/{max_retries} in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
        else:
            # All retries failed - try fallback cookie
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
            
            # Add cookies
            cookies = cookie_data.get('cookies', [])
            print(f"🍪 Adding {len(cookies)} cookies...")
            
            for cookie in cookies:
                try:
                    cookie_dict = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.youtube.com'),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                    }
                    
                    if 'expiry' in cookie:
                        cookie_dict['expiry'] = int(cookie['expiry'])
                    elif 'expirationDate' in cookie:
                        cookie_dict['expiry'] = int(cookie['expirationDate'])
                    
                    driver.add_cookie(cookie_dict)
                except:
                    pass
            
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
    seen_count = persistence.get_seen_count()
    print(f"✅ Database ready ({seen_count} videos already seen)")
    
    # Fetch videos
    channel_url = config['CHANNEL_URL']
    print(f"\n🔍 Fetching videos from channel...")
    print(f"   URL: {channel_url}")
    
    all_videos = fetch_channel_videos(channel_url, config.data, max_videos=100)
    
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
    
    # Test all cookies and filter out invalid ones
    valid_cookies = test_and_filter_cookies(active_cookies, brave_path)
    
    if not valid_cookies:
        print("\n❌ No valid (logged-in) cookies found!")
        print("   All cookies failed login test")
        print("   Please save new cookies: python scripts/save_cookies.py")
        return
    
    print(f"\n✅ Ready with {len(valid_cookies)} valid cookie sets:")
    for idx, cookie in enumerate(valid_cookies, 1):
        cookie_name = cookie.get('account_name', 'Unknown')
        print(f"   [{idx}] {cookie_name} ✓")
    
    cookie_mgr.persist()  # Save state
    
    # Track file modification time for auto-reload
    cookie_file_mtime = os.path.getmtime(config['COOKIE_DB_PATH'])
    
    # Start playing videos
    max_windows = config.get('MAX_WINDOWS', 4)
    print(f"\n🚀 Starting playback with {max_windows} concurrent windows...")
    print(f"⏱️  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📹 Videos to play: {len(unseen_videos)}")
    
    # Distribute cookies evenly across videos
    num_cookies = len(valid_cookies)
    print(f"🍪 Available cookies: {num_cookies}")
    print(f"📊 Distribution strategy: Rotating cookies evenly")
    print(f"🔄 Auto-reload: Every 10 videos or on file change")
    print("=" * 60)
    
    semaphore = asyncio.Semaphore(max_windows)
    tasks = []
    
    # Create all tasks at once - semaphore will control concurrency
    # Distribute cookies evenly: video[0]->cookie[0], video[1]->cookie[1], video[2]->cookie[0]...
    for idx, video in enumerate(unseen_videos, 1):
        # Check if we need to reload cookies (every 10 videos or file changed)
        if idx % 10 == 0 or os.path.getmtime(config['COOKIE_DB_PATH']) > cookie_file_mtime:
            print(f"\n🔄 [{idx}/{len(unseen_videos)}] Reloading cookies...")
            cookie_mgr.load()
            new_cookies = cookie_mgr.get_active_cookies()
            
            # Test only NEW cookies (not already in valid_cookies)
            existing_ids = {c.get('id') for c in valid_cookies}
            new_to_test = [c for c in new_cookies if c.get('id') not in existing_ids]
            
            if new_to_test:
                print(f"🆕 Found {len(new_to_test)} new cookies - testing...")
                newly_valid = test_and_filter_cookies(new_to_test, brave_path)
                valid_cookies.extend(newly_valid)
                num_cookies = len(valid_cookies)
                print(f"✅ Total valid cookies: {num_cookies}")
            
            cookie_file_mtime = os.path.getmtime(config['COOKIE_DB_PATH'])
        
        # Get cookie using round-robin (cycles through all cookies)
        cookie_index = (idx - 1) % num_cookies
        cookie_data = valid_cookies[cookie_index]
        
        cookie_name = cookie_data.get('account_name', 'Unknown')
        print(f"📝 Queued [{idx}/{len(unseen_videos)}]: {video['title'][:50]}...")
        print(f"   🍪 Cookie: {cookie_name} [{cookie_index + 1}/{num_cookies}]")
        
        # Create task with retry logic
        task = asyncio.create_task(
            play_video_task_with_retry(video, cookie_data, config.data, semaphore, 
                                       persistence, cookie_mgr, valid_cookies, brave_path)
        )
        tasks.append(task)
    
    print(f"\n✅ {len(tasks)} videos queued")
    print(f"⚡ Starting {max_windows} concurrent playbacks...")
    print("=" * 60)
    
    # Wait for all tasks to complete
    print(f"\n⏳ Waiting for {len(tasks)} videos to complete...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Summary
    successful = sum(1 for r in results if r is True)
    failed = len(results) - successful
    
    print("\n" + "=" * 60)
    print("📊 PLAYBACK SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {successful/len(results)*100:.1f}%")
    print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
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
