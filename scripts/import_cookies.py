"""
Import Cookies - Import cookies from portable backup file
Use this to transfer cookies from another device
"""

# Standard library imports
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Local imports
from logger_config import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)


def import_cookies(source_file: str):
    """Import cookies from a backup file"""
    
    logger.info("=" * 60)
    logger.info("COOKIE IMPORT TOOL")
    logger.info("=" * 60)
    
    print("=" * 60)
    print("📥 COOKIE IMPORT TOOL")
    print("=" * 60)
    print()
    
    # Check if source file exists
    source_path = Path(source_file)
    if not source_path.exists():
        logger.error(f"Source file not found: {source_file}")
        print(f"❌ File not found: {source_file}")
        return False
    
    # Load source cookies
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            imported_cookies = json.load(f)
        
        if not isinstance(imported_cookies, list):
            imported_cookies = [imported_cookies]
        
        logger.info(f"Loaded {len(imported_cookies)} cookie sets from {source_file}")
        print(f"✅ Loaded {len(imported_cookies)} cookie set(s) from file")
        
    except Exception as e:
        logger.error(f"Error reading source file: {e}", exc_info=True)
        print(f"❌ Error reading file: {e}")
        return False
    
    # Target file
    target_path = Path(__file__).parent.parent / "data" / "cookies.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing cookies
    existing_cookies = []
    if target_path.exists():
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                existing_cookies = json.load(f)
            logger.info(f"Found {len(existing_cookies)} existing cookie sets")
            print(f"📋 Found {len(existing_cookies)} existing cookie set(s)")
        except Exception as e:
            logger.warning(f"Could not load existing cookies: {e}")
    
    # Merge cookies
    merged_cookies = existing_cookies + imported_cookies
    
    # Save merged
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(merged_cookies, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cookies saved to: {target_path}")
        logger.info(f"Total cookie sets: {len(merged_cookies)}")
        
        print(f"\n💾 Cookies imported successfully!")
        print(f"📁 Saved to: {target_path}")
        print(f"📊 Total cookie sets: {len(merged_cookies)}")
        
        # Show imported details
        print(f"\n📦 Imported cookie details:")
        for i, cookie_set in enumerate(imported_cookies, 1):
            print(f"\n  Set {i}:")
            print(f"    - ID: {cookie_set.get('id', 'N/A')[:16]}...")
            print(f"    - Account: {cookie_set.get('account_tag', 'N/A')}")
            print(f"    - Cookies: {len(cookie_set.get('cookies', []))}")
            print(f"    - User-Agent: {cookie_set.get('user_agent', 'N/A')[:60]}...")
            print(f"    - Created: {cookie_set.get('created_at', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ IMPORT COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test cookies: python scripts/test_cookies.py")
        print("2. Run full app: python src/app.py")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving cookies: {e}", exc_info=True)
        print(f"❌ Error saving: {e}")
        return False


def main():
    """Main function"""
    
    # Check if file path provided
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📥 COOKIE IMPORT TOOL")
        print("=" * 60)
        print()
        print("Usage:")
        print(f"  python {sys.argv[0]} <cookie_file.json>")
        print()
        print("Example:")
        print(f"  python {sys.argv[0]} data/cookies_backup_20251026_223000.json")
        print()
        print("Or drag & drop a cookie backup file onto this script!")
        print()
        input("Press Enter to exit...")
        return
    
    source_file = sys.argv[1]
    
    # Import cookies
    success = import_cookies(source_file)
    
    if success:
        logger.info("Import completed successfully")
    else:
        logger.error("Import failed")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
