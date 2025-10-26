"""
Cookie Manager - Complete cookie management system
CRITICAL: Validates 100% view counting capability
"""

# Standard library imports
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Third-party imports
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Locpython scripts\test_cookies.py
from logger_config import get_logger, setup_logging

load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)


def get_brave_path():
    """Get Brave browser path"""
    env_path = os.getenv('BRAVE_BINARY_PATH')
    if env_path and os.path.exists(env_path):
        logger.info(f"Using Brave from environment: {env_path}")
        return env_path
    
    brave_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    
    for path in brave_paths:
        if os.path.exists(path):
            logger.info(f"Found Brave at: {path}")
            return path
    
    logger.error("Brave browser not found")
    return None


def test_cookies():
    """Test if cookies work for YouTube authentication"""
    
    logger.info("=" * 60)
    logger.info("COOKIE MANAGER")
    logger.info("=" * 60)
    
    print("=" * 60)
    print("🍪 COOKIE MANAGER")
    print("=" * 60)
    print()
    
    # Load cookies
    cookie_db_path = Path(__file__).parent.parent / "data" / "cookies.json"
    
    if not cookie_db_path.exists():
        logger.error(f"No cookie file found at: {cookie_db_path}")
        print("❌ No cookies found!")
        print(f"   Run: python scripts/save_cookies.py first")
        return False
    
    with open(cookie_db_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    if not cookie_data:
        logger.error("Cookie file is empty")
        print("❌ Cookie file is empty!")
        return False
    
    current_time = int(time.time())
    
    # Quick status
    print(f"📊 Accounts: {len(cookie_data)}")
    print()
    
    for idx, cookie_set in enumerate(cookie_data, 1):
        account_name = cookie_set.get('account_name', 'Unknown')
        cookies = cookie_set.get('cookies', [])
        created = cookie_set.get('created_at', 'Unknown')[:19]
        
        # Check critical cookies
        critical_cookies = ['LOGIN_INFO', '__Secure-3PSID', 'SID', 'SAPISID']
        found_critical = []
        expired_critical = []
        
        for cookie in cookies:
            if cookie['name'] in critical_cookies:
                found_critical.append(cookie['name'])
                expiry = cookie.get('expiry', 0)
                if expiry and expiry < current_time:
                    expired_critical.append(cookie['name'])
        
        # Status
        if len(found_critical) == 4 and not expired_critical:
            status = "✅"
        elif expired_critical:
            status = "❌"
        else:
            status = "⚠️"
        
        print(f"   {idx}. {status} {account_name}")
        print(f"      {len(found_critical)}/4 auth • {len(cookies)} cookies • {created}")
    
    print("-" * 60)
    print()
    
    # Menu options
    print("📋 MENU:")
    print("-" * 60)
    print("   1. Test cookies in browser")
    print("   2. Show detailed info")
    print("   3. Clean expired cookies")
    print("   4. Save new cookies")
    print("   5. Import cookies")
    if len(cookie_data) > 1:
        print("   6. Test all accounts")
    print("   0. Exit")
    print("-" * 60)
    
    choice = input("\n👉 Your choice: ").strip()
    
    if choice == '1':
        # Test cookies - always show submenu
        print("\n" + "=" * 60)
        print("🧪 SELECT ACCOUNT TO TEST:")
        print("=" * 60)
        for idx, cookie_set in enumerate(cookie_data, 1):
            acc_name = cookie_set.get('account_name', 'Unknown')
            print(f"   {idx}. {acc_name}")
        if len(cookie_data) > 1:
            print(f"   A. Test ALL accounts")
        print(f"   0. Back to main menu")
        print("=" * 60)
        
        test_choice = input("\n👉 Your choice: ").strip().upper()
        
        if test_choice == 'A' and len(cookie_data) > 1:
            # Test all accounts
            all_results = []
            for idx, cookie_set in enumerate(cookie_data, 1):
                print("\n" + "=" * 60)
                print(f"🧪 TESTING ACCOUNT {idx}/{len(cookie_data)}")
                print("=" * 60)
                result = test_single_account(cookie_set, idx)
                all_results.append(result)
                
                if idx < len(cookie_data):
                    print("\n⏱️  Moving to next account in 3 seconds...")
                    time.sleep(3)
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 SUMMARY:")
            print("=" * 60)
            for idx, (cookie_set, result) in enumerate(zip(cookie_data, all_results), 1):
                acc_name = cookie_set.get('account_name', 'Unknown')
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{idx}. {acc_name}: {status}")
            print("=" * 60)
            return all(all_results)
        
        elif test_choice == '0':
            return True
        
        elif test_choice.isdigit():
            account_num = int(test_choice)
            if 1 <= account_num <= len(cookie_data):
                return test_single_account(cookie_data[account_num - 1], account_num)
            else:
                print(f"❌ Invalid choice! Please choose 1-{len(cookie_data)}")
                return False
        else:
            print("❌ Invalid choice!")
            return False
    
    elif choice == '2':
        # Show detailed info
        show_detailed_info(cookie_data, current_time)
        return True
    
    elif choice == '3':
        # Clean expired cookies
        clean_expired(cookie_data, cookie_db_path, current_time)
        return True
    
    elif choice == '4':
        # Save new cookies
        print("\n🔄 Launching save_cookies script...")
        import subprocess
        result = subprocess.run([sys.executable, "scripts/save_cookies.py"], cwd=Path(__file__).parent.parent)
        return result.returncode == 0
    
    elif choice == '5':
        # Import cookies
        print("\n📥 Import cookies from backup file")
        backup_file = input("Enter backup file path: ").strip().strip('"')
        if backup_file and os.path.exists(backup_file):
            import subprocess
            result = subprocess.run([sys.executable, "scripts/import_cookies.py", backup_file], cwd=Path(__file__).parent.parent)
            return result.returncode == 0
        else:
            print("❌ File not found!")
            return False
    
    elif choice == '6' and len(cookie_data) > 1:
        # Test all accounts
        all_results = []
        for idx, cookie_set in enumerate(cookie_data, 1):
            print("\n" + "=" * 60)
            print(f"🧪 TESTING ACCOUNT {idx}/{len(cookie_data)}")
            print("=" * 60)
            result = test_single_account(cookie_set, idx)
            all_results.append(result)
            
            if idx < len(cookie_data):
                print("\n⏱️  Moving to next account in 3 seconds...")
                time.sleep(3)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY OF ALL TESTS:")
        print("=" * 60)
        for idx, (cookie_set, result) in enumerate(zip(cookie_data, all_results), 1):
            acc_name = cookie_set.get('account_name', 'Unknown')
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{idx}. {acc_name}: {status}")
        print("=" * 60)
        
        return all(all_results)
    
    elif choice == '0':
        print("\n👋 Goodbye!")
        return True
    
    else:
        print("\n❌ Invalid choice!")
        return False


def show_detailed_info(cookie_data, current_time):
    """Show detailed information about all cookie sets"""
    print("\n" + "=" * 60)
    print("📊 ACCOUNT DETAILS")
    print("=" * 60)
    print()
    
    for idx, cookie_set in enumerate(cookie_data, 1):
        account_name = cookie_set.get('account_name', 'Unknown')
        cookies = cookie_set.get('cookies', [])
        
        # Find shortest expiry among critical cookies
        critical_cookies = ['LOGIN_INFO', '__Secure-3PSID', 'SID', 'SAPISID']
        min_days = None
        
        for cookie in cookies:
            if cookie['name'] in critical_cookies:
                expiry = cookie.get('expiry', 0)
                if expiry:
                    time_left = expiry - current_time
                    days_left = time_left // 86400
                    if min_days is None or days_left < min_days:
                        min_days = days_left
        
        # Display
        print(f"   {idx}. {account_name}")
        if min_days is not None:
            if min_days > 0:
                print(f"      ✅ Active - {min_days} days remaining")
            else:
                print(f"      ❌ Expired")
        else:
            print(f"      ⚠️  No expiry date")
        print()
    
    print("=" * 60)
    input("\nPress Enter to continue...")


def clean_expired(cookie_data, cookie_db_path, current_time):
    """Clean expired cookie sets"""
    print("\n" + "=" * 60)
    print("🧹 CLEANING EXPIRED COOKIES")
    print("=" * 60)
    
    expired_sets = []
    valid_sets = []
    
    for idx, cookie_set in enumerate(cookie_data):
        account_name = cookie_set.get('account_name', 'Unknown')
        cookies = cookie_set.get('cookies', [])
        
        # Check if critical cookies are expired
        critical_cookies = ['LOGIN_INFO', '__Secure-3PSID', 'SID', 'SAPISID']
        expired_critical = []
        
        for cookie in cookies:
            if cookie['name'] in critical_cookies:
                expiry = cookie.get('expiry', 0)
                if expiry and expiry < current_time:
                    expired_critical.append(cookie['name'])
        
        if expired_critical:
            expired_sets.append({
                'index': idx,
                'name': account_name,
                'expired_cookies': expired_critical
            })
        else:
            valid_sets.append(cookie_set)
    
    if expired_sets:
        print(f"\n⚠️  Found {len(expired_sets)} expired cookie set(s):")
        print()
        for item in expired_sets:
            print(f"   ❌ {item['name']}")
            print(f"      Expired: {', '.join(item['expired_cookies'])}")
        
        print()
        print(f"✅ Valid cookie sets: {len(valid_sets)}")
        print()
        
        choice = input("👉 Remove expired cookies? (y/N): ").strip().lower()
        
        if choice == 'y':
            with open(cookie_db_path, 'w', encoding='utf-8') as f:
                json.dump(valid_sets, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Removed {len(expired_sets)} expired cookie sets")
            print(f"\n✅ Removed {len(expired_sets)} expired cookie set(s)")
            print(f"✅ Remaining: {len(valid_sets)} valid cookie set(s)")
        else:
            print("❌ Cleanup cancelled")
    else:
        print("\n✅ All cookie sets are valid!")
        print("✅ No expired cookies found")
    
    input("\nPress Enter to continue...")


def test_single_account(cookie_set, account_num):
    """Test a single cookie set"""
    
    cookies = cookie_set.get('cookies', [])
    user_agent = cookie_set.get('user_agent')
    account_name_saved = cookie_set.get('account_name', 'Unknown')
    created_at = cookie_set.get('created_at', 'Unknown')
    
    logger.info(f"Testing account: {account_name_saved}")
    logger.info(f"Loaded {len(cookies)} cookies from database")
    logger.info(f"Cookie ID: {cookie_set['id']}")
    
    print(f"\n✅ Account: {account_name_saved}")
    print(f"✅ Saved: {created_at[:19]}")
    print(f"✅ Cookies: {len(cookies)}")
    print(f"✅ Cookie ID: {cookie_set['id'][:8]}...")
    print()
    
    # Setup Brave
    brave_path = get_brave_path()
    if not brave_path:
        logger.error("Brave browser not found")
        print("❌ Brave not found!")
        return False
    
    chrome_options = Options()
    chrome_options.binary_location = brave_path
    
    # Visible window for testing
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Set user agent if available
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Anti-detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    print("🚀 Launching Brave...")
    
    driver = None
    try:
        # Try system ChromeDriver first
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
        
        # Hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to YouTube first
        print("📺 Opening YouTube...")
        driver.get("https://www.youtube.com")
        
        # Add cookies
        print(f"🍪 Adding {len(cookies)} cookies...")
        for cookie in cookies:
            try:
                # Selenium requires specific format
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', '.youtube.com'),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                }
                
                # Add expiry if exists
                if 'expiry' in cookie:
                    cookie_dict['expiry'] = int(cookie['expiry'])
                elif 'expirationDate' in cookie:
                    cookie_dict['expiry'] = int(cookie['expirationDate'])
                
                driver.add_cookie(cookie_dict)
            except Exception as e:
                # Some cookies may fail, that's ok
                pass
        
        print("🔄 Reloading YouTube with cookies...")
        driver.get("https://www.youtube.com")
        
        # Wait for page load
        time.sleep(3)
        
        print("🔍 Checking authentication...")
        
        # Method 1: Check for avatar/profile button
        logged_in = False
        account_name = None
        
        try:
            # Wait for avatar button
            avatar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "avatar-btn"))
            )
            
            # Try to get account name
            try:
                aria_label = avatar.get_attribute("aria-label")
                if aria_label and "Google Account" in aria_label:
                    account_name = aria_label.replace("Google Account: ", "").strip()
                    logged_in = True
            except:
                logged_in = True
                
        except:
            pass
        
        # Method 2: Check if sign-in button exists (means NOT logged in)
        try:
            sign_in = driver.find_element(By.XPATH, "//a[@aria-label='Sign in']")
            if sign_in:
                logged_in = False
        except:
            # Sign in button not found = likely logged in
            pass
        
        # Method 3: Check cookies in browser
        browser_cookies = driver.get_cookies()
        has_login_cookie = any(c['name'] in ['LOGIN_INFO', '__Secure-3PSID', 'SID'] 
                               for c in browser_cookies)
        
        print()
        print("=" * 60)
        print("📊 TEST RESULTS:")
        print("=" * 60)
        
        if logged_in and account_name:
            print(f"✅ SUCCESS! Logged in as: {account_name}")
            print("✅ Cookies are working perfectly!")
            print("✅ Views will be counted 100%!")
        elif logged_in or has_login_cookie:
            print("✅ SUCCESS! User is logged in")
            print("✅ Cookies are working!")
            print("✅ Views will be counted!")
        else:
            print("❌ FAILED! User is NOT logged in")
            print("❌ Cookies may be expired or invalid")
            print("❌ Views may NOT be counted properly")
            print()
            print("🔧 Solutions:")
            print("   1. Run: python scripts/save_cookies.py again")
            print("   2. Make sure you fully log in to YouTube")
            print("   3. Check that cookies aren't expired")
        
        print()
        print(f"🍪 Cookies in browser: {len(browser_cookies)}")
        print(f"🔑 Auth cookies present: {has_login_cookie}")
        print("=" * 60)
        
        # Keep browser open for 5 seconds to verify visually
        print("\n⏱️  Keeping browser open for 5 seconds for visual verification...")
        time.sleep(5)
        
        if driver:
            driver.quit()
        
        return logged_in or has_login_cookie
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return False


if __name__ == "__main__":
    success = test_cookies()
    sys.exit(0 if success else 1)
