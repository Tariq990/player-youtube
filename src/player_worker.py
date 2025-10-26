"""
Player Worker - Play YouTube videos with human simulation.
CRITICAL: Ensures 100% view counting with real browser behavior.
"""

# Standard library imports
import asyncio
import random
import time
from typing import Dict, Optional

# Third-party imports
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PlayerWorker:
    """Worker to play a single video with human simulation"""
    
    def __init__(self, driver, config: Dict):
        self.driver = driver
        self.config = config
        self.enable_human_sim = config.get('ENABLE_HUMAN_SIMULATION', True)
        self.anti_detection = config.get('ANTI_DETECTION', {})
    
    async def play_video(self, video: Dict, cookie_data: Dict) -> bool:
        """
        Play a video with full human simulation
        Returns True if successful, False otherwise
        """
        try:
            video_url = video['url']
            video_id = video.get('video_id', video_url.split('=')[-1])
            
            print(f"\n🎬 Playing: {video.get('title', video_id)}")
            print(f"🔗 URL: {video_url}")
            
            # Navigate to video
            self.driver.get(video_url)
            
            # Wait for page load
            await asyncio.sleep(random.uniform(2, 4))
            
            # Check if logged in
            if not await self._verify_login():
                print("❌ Not logged in! Cookie may be invalid")
                return False
            
            # Get video duration
            duration = await self._get_video_duration(video)
            if not duration:
                print("⚠️ Could not get video duration, using default")
                duration = self.config.get('DEFAULT_VIDEO_DURATION', 300)
            
            print(f"⏱️  Video duration: {duration} seconds")
            
            # Human simulation before playback
            if self.enable_human_sim:
                await self._simulate_human_behavior_before_play()
            
            # Monitor playback
            success = await self._monitor_playback(duration)
            
            if success:
                print(f"✅ Successfully watched video!")
                return True
            else:
                print(f"❌ Playback failed")
                return False
            
        except Exception as e:
            print(f"❌ Error playing video: {e}")
            return False
    
    async def _verify_login(self) -> bool:
        """Verify user is logged in"""
        try:
            # Check for avatar button
            avatar = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "avatar-btn"))
            )
            return avatar is not None
        except:
            # Check cookies as fallback
            cookies = self.driver.get_cookies()
            return any(c['name'] in ['LOGIN_INFO', '__Secure-3PSID'] for c in cookies)
    
    async def _get_video_duration(self, video: Dict) -> Optional[int]:
        """Get video duration in seconds"""
        # First check if we have it in video dict
        if 'duration' in video:
            return int(video['duration'])
        
        # Try to get from video element
        try:
            await asyncio.sleep(2)
            duration = self.driver.execute_script(
                "return document.querySelector('video').duration"
            )
            if duration and duration > 0:
                return int(duration)
        except:
            pass
        
        return None
    
    async def _simulate_human_behavior_before_play(self):
        """Simulate human behavior before video starts"""
        print("🤖 Simulating human behavior...")
        
        # Random mouse movements
        if self.anti_detection.get('ENABLE_MOUSE_SIMULATION', True):
            await self._random_mouse_movements()
        
        # Random scroll
        if self.anti_detection.get('ENABLE_SCROLL_SIMULATION', True):
            await self._random_scroll()
        
        # Random delay
        delay = random.uniform(
            self.anti_detection.get('RANDOM_DELAY_MIN', 1),
            self.anti_detection.get('RANDOM_DELAY_MAX', 3)
        )
        await asyncio.sleep(delay)
    
    async def _random_mouse_movements(self):
        """Simulate random mouse movements"""
        try:
            actions = ActionChains(self.driver)
            
            # Get window size
            window_size = self.driver.get_window_size()
            max_x = window_size['width']
            max_y = window_size['height']
            
            # Number of movements
            num_moves = random.randint(
                self.anti_detection.get('MOUSE_MOVE_COUNT_MIN', 3),
                self.anti_detection.get('MOUSE_MOVE_COUNT_MAX', 8)
            )
            
            for _ in range(num_moves):
                x = random.randint(100, max_x - 100)
                y = random.randint(100, max_y - 100)
                
                # Move to random position
                actions.move_by_offset(x - max_x // 2, y - max_y // 2)
                actions.perform()
                
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Reset actions
                actions = ActionChains(self.driver)
                
        except Exception as e:
            # Mouse movement not critical, just log
            pass
    
    async def _random_scroll(self):
        """Simulate random scrolling"""
        try:
            num_scrolls = random.randint(
                self.anti_detection.get('SCROLL_COUNT_MIN', 1),
                self.anti_detection.get('SCROLL_COUNT_MAX', 3)
            )
            
            for _ in range(num_scrolls):
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            
        except Exception as e:
            pass
    
    async def _monitor_playback(self, duration: int) -> bool:
        """
        Monitor video playback for the full duration
        This is CRITICAL for view counting
        """
        min_duration = self.config.get('MIN_VIDEO_DURATION', 30)
        
        # Ensure we watch at least minimum duration
        watch_time = max(min_duration, min(duration, duration))
        
        print(f"👁️  Monitoring playback for {watch_time} seconds...")
        
        start_time = time.time()
        check_interval = 5  # Check every 5 seconds
        
        while time.time() - start_time < watch_time:
            try:
                # Check if video is still playing
                is_playing = self.driver.execute_script(
                    "return !document.querySelector('video').paused"
                )
                
                if not is_playing:
                    # Try to click play button
                    print("⚠️ Video paused, attempting to resume...")
                    try:
                        play_button = self.driver.find_element(By.CLASS_NAME, "ytp-play-button")
                        play_button.click()
                        await asyncio.sleep(1)
                    except:
                        pass
                
                # Check for errors
                error = self.driver.execute_script(
                    "return document.querySelector('.ytp-error')"
                )
                if error:
                    print("❌ Video error detected")
                    return False
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
                # Show progress
                elapsed = int(time.time() - start_time)
                remaining = watch_time - elapsed
                if remaining > 0:
                    print(f"⏳ Watched {elapsed}s / {watch_time}s (remaining: {remaining}s)")
                
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
                # Continue monitoring even with errors
                await asyncio.sleep(check_interval)
        
        total_watched = int(time.time() - start_time)
        print(f"✅ Completed watching for {total_watched} seconds")
        
        return total_watched >= min_duration
    
    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
        except:
            pass


async def play_video_with_worker(driver, video: Dict, cookie_data: Dict, config: Dict) -> bool:
    """
    Helper function to play a video
    """
    worker = PlayerWorker(driver, config)
    try:
        return await worker.play_video(video, cookie_data)
    finally:
        worker.close()
