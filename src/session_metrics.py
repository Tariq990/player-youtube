"""
Session Metrics - Track and report session statistics
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class SessionMetrics:
    """Track session statistics and metrics"""
    
    videos_watched: int = 0
    videos_failed: int = 0
    total_watch_time: int = 0  # seconds
    cookies_used: Dict[str, int] = field(default_factory=dict)
    errors: List[Dict] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    
    def record_success(self, video_id: str, cookie_id: str, watch_time: int):
        """Record successful video playback"""
        self.videos_watched += 1
        self.total_watch_time += watch_time
        
        if cookie_id not in self.cookies_used:
            self.cookies_used[cookie_id] = 0
        self.cookies_used[cookie_id] += 1
    
    def record_failure(self, video_id: str, cookie_id: str, error: str):
        """Record failed video playback"""
        self.videos_failed += 1
        self.errors.append({
            'video_id': video_id,
            'cookie_id': cookie_id,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.videos_watched + self.videos_failed
        if total == 0:
            return 0.0
        return (self.videos_watched / total) * 100
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_avg_video_length(self) -> float:
        """Get average video length in minutes"""
        if self.videos_watched == 0:
            return 0.0
        return (self.total_watch_time / self.videos_watched) / 60
    
    def report(self):
        """Print comprehensive session report"""
        elapsed = self.get_elapsed_time()
        success_rate = self.get_success_rate()
        avg_length = self.get_avg_video_length()
        
        print("\n" + "=" * 60)
        print("📊 SESSION SUMMARY")
        print("=" * 60)
        print(f"⏱️  Total Runtime: {elapsed/3600:.2f} hours ({elapsed/60:.1f} minutes)")
        print(f"✅ Videos Watched: {self.videos_watched}")
        print(f"❌ Videos Failed: {self.videos_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🎬 Total Watch Time: {self.total_watch_time/3600:.2f} hours")
        print(f"📏 Avg Video Length: {avg_length:.1f} minutes")
        
        if self.cookies_used:
            print("\n🍪 Cookie Usage:")
            for cookie_id, count in sorted(self.cookies_used.items(), key=lambda x: x[1], reverse=True):
                print(f"   {cookie_id}: {count} videos")
        
        if self.errors:
            print(f"\n⚠️  Errors Encountered: {len(self.errors)}")
            # Show last 5 errors
            recent_errors = self.errors[-5:]
            for error in recent_errors:
                print(f"   - {error['video_id']}: {error['error'][:50]}...")
        
        # Calculate throughput
        if elapsed > 0:
            videos_per_hour = (self.videos_watched / elapsed) * 3600
            print(f"\n⚡ Throughput: {videos_per_hour:.1f} videos/hour")
        
        print("=" * 60)
    
    def quick_status(self):
        """Print quick status update"""
        total = self.videos_watched + self.videos_failed
        success_rate = self.get_success_rate()
        print(f"📊 Status: {self.videos_watched}/{total} videos ({success_rate:.0f}% success)")
