"""
Persistence - SQLite database for seen videos tracking.
Handles all database operations with proper error handling.
"""

# Standard library imports
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

# No third-party imports needed


class Persistence:
    """Manage seen videos database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_videos (
                video_id TEXT PRIMARY KEY,
                last_seen TIMESTAMP,
                times_seen INTEGER DEFAULT 1,
                title TEXT,
                duration INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_seen(self, video_id: str) -> bool:
        """Check if video has been seen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT video_id FROM seen_videos WHERE video_id = ?', (video_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_seen(self, video_id: str, title: str = "", duration: int = 0):
        """Mark video as seen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute('SELECT times_seen FROM seen_videos WHERE video_id = ?', (video_id,))
        result = cursor.fetchone()
        
        if result:
            # Update existing
            times_seen = result[0] + 1
            cursor.execute('''
                UPDATE seen_videos 
                SET last_seen = ?, times_seen = ?
                WHERE video_id = ?
            ''', (datetime.now(), times_seen, video_id))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO seen_videos (video_id, last_seen, times_seen, title, duration)
                VALUES (?, ?, 1, ?, ?)
            ''', (video_id, datetime.now(), title, duration))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Marked as seen: {video_id}")
    
    def get_seen_count(self) -> int:
        """Get total number of seen videos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM seen_videos')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_unseen_videos(self, all_videos: List[dict]) -> List[dict]:
        """Filter out videos that have been seen"""
        unseen = []
        for video in all_videos:
            if not self.is_seen(video['video_id']):
                unseen.append(video)
        return unseen
    
    def clear_all(self):
        """Clear all seen videos (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM seen_videos')
        
        conn.commit()
        conn.close()
        
        print("🗑️  Cleared all seen videos")
