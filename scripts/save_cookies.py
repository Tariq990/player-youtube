"""
Save Cookies from Brave Browser
This script opens Brave, lets you login to YouTube, then saves all cookies
CRITICAL: Ensures 100% view counting by using real browser cookies
"""

# Standard library imports
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Third-party imports
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Local imports
from logger_config import get_logger, setup_logging

load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)


def get_brave_path():
    """Get Brave browser executable path"""
    # Try environment variable first
    env_path = os.getenv('BRAVE_BINARY_PATH')
    if env_path and os.path.exists(env_path):
        logger.info(f"Using Brave from environment: {env_path}")
        return env_path
    
    # Common Windows paths
    brave_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    
    for path in brave_paths:
        if os.path.exists(path):
            logger.info(f"Found Brave at: {path}")
            return path
    
    logger.error("Brave browser not found in default locations")
    return None


def save_cookies_from_brave():
    """Open Brave, login to YouTube, and save cookies"""
    
    logger.info("=" * 60)
    logger.info("BRAVE BROWSER COOKIE SAVER")
    logger.info("=" * 60)
    
    print("=" * 60)
    print("🦁 BRAVE BROWSER COOKIE SAVER")
    print("=" * 60)
    print()
    
    # Get Brave path
    brave_path = get_brave_path()
    if not brave_path:
        logger.error("Brave browser not found")
        print("❌ Brave browser not found!")
        print("Please install Brave or set BRAVE_BINARY_PATH in .env")
        return
    
    print(f"✅ Found Brave: {brave_path}")
    print()
    
    # Setup Brave with Selenium
    chrome_options = Options()
    chrome_options.binary_location = brave_path
    
    # Use VISIBLE window (not headless) for login
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Disable automation flags to look like real browser
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    logger.info("Launching Brave browser...")
    print("🚀 Launching Brave browser...")
    print()
    
    driver = None
    try:
        # Try to use ChromeDriver without webdriver-manager
        try:
            logger.info("Attempting to use system ChromeDriver...")
            chrome_options.binary_location = brave_path
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"System ChromeDriver failed: {e}")
            logger.info("Trying with webdriver-manager...")
            # Fallback to webdriver-manager
            service = Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Go to YouTube
        logger.info("Navigating to YouTube...")
        print("📺 Opening YouTube...")
        driver.get("https://www.youtube.com")
        
        print()
        print("=" * 60)
        print("⚠️  IMPORTANT INSTRUCTIONS:")
        print("=" * 60)
        print("1. ✅ Login to your YouTube account in the browser")
        print("2. ✅ Make sure you see your profile picture/avatar")
        print("3. ✅ Return to this terminal")
        print("4. ✅ Press ENTER to save cookies")
        print("=" * 60)
        print()
        
        logger.info("Waiting for user to log in...")
        input("Press ENTER after logging in... ")
        
        # Get all cookies
        logger.info("Extracting cookies...")
        cookies = driver.get_cookies()
        
        # Get User-Agent
        user_agent = driver.execute_script("return navigator.userAgent")
        
        logger.info(f"Extracted {len(cookies)} cookies")
        logger.info(f"User-Agent: {user_agent}")
        
        print(f"\n✅ Found {len(cookies)} cookies")
        print(f"✅ User-Agent: {user_agent[:80]}...")
        
        # ===== CRITICAL CHECK: Validate authentication cookies =====
        print(f"\n🔍 Validating authentication cookies...")
        
        # Check for critical authentication cookies
        critical_cookies = ['LOGIN_INFO', '__Secure-3PSID', 'SID', 'SAPISID']
        found_critical = [c['name'] for c in cookies if c['name'] in critical_cookies]
        
        if not found_critical:
            logger.error("NO authentication cookies found!")
            print(f"\n❌ ERROR: NO authentication cookies found!")
            print(f"❌ You are NOT logged in to YouTube!")
            print(f"\n🔧 Please:")
            print(f"   1. Make sure you see your profile picture in the browser")
            print(f"   2. Click on your avatar to verify you're logged in")
            print(f"   3. Try logging out and logging in again")
            print(f"\n⚠️  Saving these cookies will NOT work for view counting!")
            
            choice = input("\n👉 Continue saving anyway? (y/N): ").strip().lower()
            if choice != 'y':
                logger.info("User cancelled save due to missing auth cookies")
                print(f"❌ Save cancelled")
                return
        
        # Show which critical cookies were found
        print(f"✅ Found authentication cookies:")
        for cookie_name in found_critical:
            print(f"   • {cookie_name}")
        
        if len(found_critical) < 3:
            logger.warning(f"Only {len(found_critical)}/4 critical cookies found")
            print(f"\n⚠️  WARNING: Only {len(found_critical)}/4 critical cookies found")
            print(f"⚠️  Missing: {', '.join(set(critical_cookies) - set(found_critical))}")
            print(f"⚠️  These cookies may not work properly!")
            
            choice = input("\n👉 Continue saving? (y/N): ").strip().lower()
            if choice != 'y':
                logger.info("User cancelled save due to incomplete auth cookies")
                print(f"❌ Save cancelled")
                return
        
        # Save to file
        cookie_db_path = Path(__file__).parent.parent / "data" / "cookies.json"
        cookie_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Also create portable backup with timestamp
        portable_backup_path = Path(__file__).parent.parent / "data" / f"cookies_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Load existing or create new
        if cookie_db_path.exists():
            with open(cookie_db_path, 'r', encoding='utf-8') as f:
                try:
                    existing_cookies = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load existing cookies: {e}")
                    existing_cookies = []
        else:
            existing_cookies = []
        
        # Check for duplicates based on PREF cookie (stable account identifier)
        # PREF cookie contains timezone and preferences - it's UNIQUE per Google account
        # Even if you login 100 times with same account, PREF stays the same!
        current_pref = None
        for cookie in cookies:
            if cookie['name'] == 'PREF':
                current_pref = cookie['value']
                break
        
        duplicate_found = False
        duplicate_index = -1
        
        if current_pref:
            print(f"\n🔍 Checking for duplicates...")
            print(f"   🔑 Account ID (PREF): {current_pref[:40]}...")
            
            for idx, existing_set in enumerate(existing_cookies):
                existing_pref = None
                for cookie in existing_set.get('cookies', []):
                    if cookie['name'] == 'PREF':
                        existing_pref = cookie['value']
                        break
                
                if existing_pref == current_pref:
                    duplicate_found = True
                    duplicate_index = idx
                    logger.info(f"Found duplicate account: {existing_set.get('account_name', 'Unknown')}")
                    print(f"   ✅ Found same account!")
                    print(f"   💡 PREF Cookie matches = Same Google account")
                    break
            
            if not duplicate_found:
                print(f"   ✅ New account - Different PREF")
        
        # Ask for account name
        if duplicate_found:
            # Use existing name for duplicate
            account_name = existing_cookies[duplicate_index].get('account_name', f"YouTube_Account_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        else:
            # New account - ask for name
            print(f"\n📝 Name your new account:")
            print(f"   💡 Enter a unique name (or press Enter for auto-generated name)")
            print(f"   Example: My Main Channel, Test Account, Gaming Channel")
            
            custom_name = input("\n👉 Account name: ").strip()
            
            if custom_name:
                account_name = custom_name
                print(f"   ✅ Done: {account_name}")
            else:
                account_name = f"YouTube_Account_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"   ℹ️  Using auto-generated name: {account_name}")
        
        # Create cookie database entry
        cookie_entry = {
            "id": str(uuid.uuid4()),
            "account_name": account_name,
            "account_tag": account_name.lower().replace(' ', '_'),
            "source": "brave_selenium",
            "user_agent": user_agent,
            "cookies": cookies,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "usage_count": 0,
            "last_used": None,
            "notes": f"Account: {account_name} - Saved from Brave browser"
        }
        
        # Handle duplicate or new account
        if duplicate_found:
            existing_account_name = existing_cookies[duplicate_index].get('account_name', 'Unknown')
            print(f"\n⚠️  Warning: Found existing cookies for same account!")
            print(f"   Previous account: {existing_account_name}")
            print(f"   Previous save date: {existing_cookies[duplicate_index]['created_at']}")
            print(f"\n   What do you want to do?")
            print(f"   1. Replace old cookies with new (recommended)")
            print(f"   2. Keep both (saves 2 copies)")
            print(f"   3. Cancel save")
            
            choice = input("\n👉 Your choice (1/2/3): ").strip()
            
            if choice == '1':
                # Replace old with new
                existing_cookies[duplicate_index] = cookie_entry
                logger.info(f"Replaced duplicate cookie set at index {duplicate_index}")
                print(f"✅ Replaced old cookies")
            elif choice == '2':
                # Keep both
                existing_cookies.append(cookie_entry)
                logger.info("Keeping both cookie sets")
                print(f"✅ Saved both cookie sets")
            else:
                # Cancel
                logger.info("Save cancelled by user")
                print(f"❌ Save cancelled")
                return
        else:
            # No duplicate, add new
            existing_cookies.append(cookie_entry)
            logger.info("No duplicate found, adding new cookie set")
        
        # Save main file
        with open(cookie_db_path, 'w', encoding='utf-8') as f:
            json.dump(existing_cookies, f, indent=2, ensure_ascii=False)
        
        # Save portable backup (can be transferred to other devices)
        with open(portable_backup_path, 'w', encoding='utf-8') as f:
            json.dump([cookie_entry], f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cookies saved to: {cookie_db_path}")
        logger.info(f"Portable backup saved to: {portable_backup_path}")
        logger.info(f"Total cookie sets in database: {len(existing_cookies)}")
        
        print(f"\n💾 Cookies saved to: {cookie_db_path}")
        print(f"📦 Portable backup: {portable_backup_path}")
        print(f"📊 Total cookie sets: {len(existing_cookies)}")
        
        # Show all accounts
        if len(existing_cookies) > 1:
            print(f"\n📋 Saved Accounts:")
            for idx, cookie_set in enumerate(existing_cookies, 1):
                acc_name = cookie_set.get('account_name', 'Unknown')
                created = cookie_set['created_at'][:19]
                num_cookies = len(cookie_set['cookies'])
                print(f"   {idx}. {acc_name}")
                print(f"      • Saved: {created}")
                print(f"      • Cookies: {num_cookies}")
        
        print("\n" + "=" * 60)
        print("✅ DONE! Cookies saved successfully")
        print("=" * 60)
        print("\n📦 HOW TO USE ON ANOTHER DEVICE:")
        print("=" * 60)
        print(f"1. Copy the portable backup file:")
        print(f"   {portable_backup_path}")
        print(f"")
        print(f"2. On the new device, put it in: data/cookies.json")
        print(f"")
        print(f"3. The file contains:")
        print(f"   - {len(cookies)} cookies")
        print(f"   - User-Agent: {user_agent[:50]}...")
        print(f"   - Authentication data")
        print(f"")
        print(f"4. No need to login again! Just run:")
        print(f"   python scripts/test_cookies.py")
        print(f"   python src/app.py")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test cookies: python scripts/test_cookies.py")
        print("2. Run full app: python src/app.py")
        print()
        
    except Exception as e:
        logger.error(f"Error saving cookies: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    save_cookies_from_brave()
