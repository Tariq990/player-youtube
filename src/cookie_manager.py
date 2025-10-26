"""
Cookie Manager - Manage, rotate, and validate cookies with encryption.
CRITICAL: Supports Brave Browser cookie extraction.
"""

# Standard library imports
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Get logger
logger = logging.getLogger(__name__)


class CookieManager:
    """Manage YouTube cookies with encryption and rotation"""
    
    def __init__(self, cookie_db_path: str):
        self.cookie_db_path = cookie_db_path
        self.cookies: List[Dict] = []
        self.rotation_index = 0
        
        # Setup encryption
        key = os.getenv('ENCRYPTION_KEY')
        if key:
            try:
                self.cipher = Fernet(key.encode())
                self.encryption_enabled = True
                logger.info("Cookie encryption enabled")
            except Exception as e:
                logger.warning(f"Invalid encryption key, encryption disabled: {e}")
                self.encryption_enabled = False
        else:
            logger.info("No encryption key found, encryption disabled")
            self.encryption_enabled = False
        
        # Load cookies
        self.load()
    
    def load(self):
        """Load cookies from database"""
        if not os.path.exists(self.cookie_db_path):
            logger.info(f"No cookie database found at {self.cookie_db_path}")
            self.cookies = []
            return
        
        try:
            with open(self.cookie_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Decrypt if needed
            if self.encryption_enabled and isinstance(data, list):
                for cookie in data:
                    if 'value' in cookie and cookie.get('encrypted', False):
                        try:
                            cookie['value'] = self.cipher.decrypt(
                                cookie['value'].encode()
                            ).decode()
                            cookie['encrypted'] = False
                        except Exception as e:
                            logger.error(f"Failed to decrypt cookie: {e}")
            
            self.cookies = data if isinstance(data, list) else []
            logger.info(f"Loaded {len(self.cookies)} cookies from database")
            
        except Exception as e:
            logger.error(f"Error loading cookies: {e}", exc_info=True)
            self.cookies = []
    
    def persist(self):
        """Save cookies to database"""
        try:
            # Encrypt sensitive data if enabled
            data_to_save = []
            for cookie in self.cookies:
                cookie_copy = cookie.copy()
                if self.encryption_enabled and 'value' in cookie_copy:
                    cookie_copy['value'] = self.cipher.encrypt(
                        cookie_copy['value'].encode()
                    ).decode()
                    cookie_copy['encrypted'] = True
                data_to_save.append(cookie_copy)
            
            # Ensure directory exists
            Path(self.cookie_db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cookie_db_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
            
            logger.info(f"Saved {len(self.cookies)} cookies to database")
            
        except Exception as e:
            logger.error(f"Error saving cookies: {e}", exc_info=True)
    
    def add_cookie(self, cookie: Dict, overwrite: bool = False):
        """Add a cookie to the database"""
        cookie_id = cookie.get('id') or str(uuid.uuid4())
        cookie['id'] = cookie_id
        
        # Set defaults
        cookie.setdefault('status', 'active')
        cookie.setdefault('usage_count', 0)
        cookie.setdefault('last_used', None)
        cookie.setdefault('created_at', datetime.now().isoformat())
        
        # Check if exists
        existing = [c for c in self.cookies if c['id'] == cookie_id]
        if existing:
            if overwrite:
                self.cookies = [c for c in self.cookies if c['id'] != cookie_id]
                self.cookies.append(cookie)
                logger.info(f"Cookie {cookie_id[:8]}... overwritten")
            else:
                logger.warning(f"Cookie {cookie_id[:8]}... already exists")
        else:
            self.cookies.append(cookie)
            logger.debug(f"Cookie {cookie_id[:8]}... added")
    
    def get_active_cookies(self) -> List[Dict]:
        """Get all active (valid) cookies"""
        return [c for c in self.cookies if c.get('status') == 'active']
    
    def rotate_cookie(self, domain: str = ".youtube.com", policy: str = "round_robin") -> Optional[Dict]:
        """
        Get next cookie using rotation policy.
        
        DEBUG CHECKPOINT: Set breakpoint to inspect rotation logic
        - active_cookies: List of available cookies
        - policy: Current rotation strategy
        - self.rotation_index: Current position in round-robin
        
        Args:
            domain: Cookie domain (default: .youtube.com)
            policy: Rotation policy ('round_robin', 'least_used', or 'failover')
            
        Returns:
            Dict: Next cookie to use, or None if no active cookies
        """
        active_cookies = self.get_active_cookies()
        
        # DEBUG: Check if we have any active cookies
        if not active_cookies:
            logger.error("No active cookies available for rotation")
            return None
        
        # DEBUG CHECKPOINT: Examine rotation logic
        # Inspect: active_cookies, len(active_cookies), policy
        if policy == "round_robin":
            cookie = active_cookies[self.rotation_index % len(active_cookies)]
            self.rotation_index += 1
        elif policy == "least_used":
            cookie = min(active_cookies, key=lambda c: c.get('usage_count', 0))
        else:
            cookie = active_cookies[0]
        
        logger.debug(f"Rotated to cookie {cookie['id'][:8]}... (policy: {policy})")
        return cookie
    
    def mark_used(self, cookie_id: str):
        """Mark cookie as used"""
        for cookie in self.cookies:
            if cookie['id'] == cookie_id:
                cookie['usage_count'] = cookie.get('usage_count', 0) + 1
                cookie['last_used'] = datetime.now().isoformat()
                break
    
    def mark_invalid(self, cookie_id: str):
        """Mark cookie as invalid"""
        for cookie in self.cookies:
            if cookie['id'] == cookie_id:
                cookie['status'] = 'invalid'
                logger.warning(f"Cookie {cookie_id[:8]}... marked as invalid")
                break
    
    def delete_cookie(self, cookie_id: str):
        """Delete cookie permanently from database"""
        self.cookies = [c for c in self.cookies if c.get('id') != cookie_id]
        logger.warning(f"Cookie {cookie_id[:8]}... deleted permanently")
    
    def quarantine(self, cookie_id: str, duration: int = 3600):
        """Put cookie in quarantine"""
        for cookie in self.cookies:
            if cookie['id'] == cookie_id:
                cookie['status'] = 'quarantine'
                cookie['quarantine_until'] = (
                    datetime.now() + timedelta(seconds=duration)
                ).isoformat()
                logger.warning(f"Cookie {cookie_id[:8]}... quarantined for {duration}s")
                break
    
    def get_cookie_summary(self) -> Dict:
        """Get summary of cookie status"""
        return {
            'total': len(self.cookies),
            'active': len([c for c in self.cookies if c.get('status') == 'active']),
            'invalid': len([c for c in self.cookies if c.get('status') == 'invalid']),
            'quarantine': len([c for c in self.cookies if c.get('status') == 'quarantine']),
        }
