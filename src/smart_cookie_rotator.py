"""
Smart Cookie Rotation
Intelligent cookie selection based on health scores and usage patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CookieHealth:
    """Track health metrics for a cookie."""
    cookie_id: str
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    average_watch_time: float = 0.0
    total_watch_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_uses == 0:
            return 1.0  # New cookies start with full score
        return self.successful_uses / self.total_uses
    
    @property
    def health_score(self) -> float:
        """
        Calculate overall health score (0.0 to 100.0).
        Considers multiple factors.
        """
        # Base score from success rate
        score = self.success_rate * 100
        
        # Penalty for consecutive failures
        if self.consecutive_failures > 0:
            penalty = min(self.consecutive_failures * 10, 50)
            score -= penalty
        
        # Bonus for recent success
        if self.last_success:
            hours_since_success = (datetime.now() - self.last_success).total_seconds() / 3600
            if hours_since_success < 1:
                score += 10
            elif hours_since_success < 24:
                score += 5
        
        # Penalty for recent failure
        if self.last_failure:
            hours_since_failure = (datetime.now() - self.last_failure).total_seconds() / 3600
            if hours_since_failure < 1:
                score -= 20
            elif hours_since_failure < 24:
                score -= 10
        
        return max(0.0, min(100.0, score))
    
    @property
    def is_healthy(self) -> bool:
        """Check if cookie is healthy enough to use."""
        return (
            self.health_score >= 30.0 and
            self.consecutive_failures < 5
        )


class SmartCookieRotator:
    """Intelligent cookie rotation with health tracking."""
    
    def __init__(
        self,
        cookies: List[Dict],
        min_health_score: float = 30.0,
        max_consecutive_failures: int = 5
    ):
        """
        Initialize smart cookie rotator.
        
        Args:
            cookies: List of cookie dictionaries
            min_health_score: Minimum health score to use cookie
            max_consecutive_failures: Max failures before blocking cookie
        """
        self.cookies = cookies
        self.min_health_score = min_health_score
        self.max_consecutive_failures = max_consecutive_failures
        
        # Track health for each cookie
        self.health: Dict[str, CookieHealth] = {}
        for cookie in cookies:
            cookie_id = cookie.get('id', cookie.get('name', str(id(cookie))))
            self.health[cookie_id] = CookieHealth(cookie_id=cookie_id)
        
        self._current_index = 0
    
    def get_next_cookie(self) -> Optional[Dict]:
        """
        Get next cookie using smart selection.
        Prioritizes healthy cookies with lowest usage.
        """
        if not self.cookies:
            return None
        
        # Get healthy cookies sorted by health score (descending)
        healthy_cookies = [
            (cookie, self.health[self._get_cookie_id(cookie)])
            for cookie in self.cookies
            if self._is_cookie_healthy(cookie)
        ]
        
        if not healthy_cookies:
            logger.warning("No healthy cookies available!")
            return None
        
        # Sort by:
        # 1. Health score (descending)
        # 2. Total uses (ascending - prefer less used)
        # 3. Last success time (descending - prefer recently successful)
        healthy_cookies.sort(
            key=lambda x: (
                -x[1].health_score,  # Higher score first
                x[1].total_uses,      # Lower usage first
                -(x[1].last_success.timestamp() if x[1].last_success else 0)  # Recent success first
            )
        )
        
        # Return best cookie
        best_cookie = healthy_cookies[0][0]
        cookie_id = self._get_cookie_id(best_cookie)
        health = self.health[cookie_id]
        
        logger.info(
            f"Selected cookie {cookie_id}: "
            f"health={health.health_score:.1f}, "
            f"uses={health.total_uses}, "
            f"success_rate={health.success_rate*100:.1f}%"
        )
        
        return best_cookie
    
    def record_success(
        self,
        cookie: Dict,
        watch_time: float = 0.0
    ) -> None:
        """Record successful use of cookie."""
        cookie_id = self._get_cookie_id(cookie)
        health = self.health.get(cookie_id)
        
        if not health:
            return
        
        health.total_uses += 1
        health.successful_uses += 1
        health.last_success = datetime.now()
        health.consecutive_failures = 0  # Reset failure counter
        
        if watch_time > 0:
            health.total_watch_time += watch_time
            health.average_watch_time = health.total_watch_time / health.successful_uses
        
        logger.info(
            f"Cookie {cookie_id} success: "
            f"health={health.health_score:.1f}, "
            f"success_rate={health.success_rate*100:.1f}%"
        )
    
    def record_failure(
        self,
        cookie: Dict,
        error: Optional[str] = None
    ) -> None:
        """Record failed use of cookie."""
        cookie_id = self._get_cookie_id(cookie)
        health = self.health.get(cookie_id)
        
        if not health:
            return
        
        health.total_uses += 1
        health.failed_uses += 1
        health.last_failure = datetime.now()
        health.consecutive_failures += 1
        
        logger.warning(
            f"Cookie {cookie_id} failure: "
            f"health={health.health_score:.1f}, "
            f"consecutive_failures={health.consecutive_failures}, "
            f"error={error or 'unknown'}"
        )
    
    def get_health_report(self) -> str:
        """Get comprehensive health report for all cookies."""
        report = ["\n" + "=" * 60]
        report.append("🍪 COOKIE HEALTH REPORT")
        report.append("=" * 60)
        
        # Sort by health score
        sorted_health = sorted(
            self.health.items(),
            key=lambda x: x[1].health_score,
            reverse=True
        )
        
        for cookie_id, health in sorted_health:
            status = "✅" if health.is_healthy else "❌"
            report.append(f"\n{status} Cookie: {cookie_id}")
            report.append(f"   Health Score: {health.health_score:.1f}/100")
            report.append(f"   Success Rate: {health.success_rate*100:.1f}%")
            report.append(f"   Total Uses: {health.total_uses}")
            report.append(f"   Consecutive Failures: {health.consecutive_failures}")
            
            if health.last_success:
                hours_ago = (datetime.now() - health.last_success).total_seconds() / 3600
                report.append(f"   Last Success: {hours_ago:.1f} hours ago")
            
            if health.average_watch_time > 0:
                report.append(f"   Avg Watch Time: {health.average_watch_time:.1f}s")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def get_healthy_count(self) -> int:
        """Get count of healthy cookies."""
        return sum(1 for h in self.health.values() if h.is_healthy)
    
    def reset_cookie_health(self, cookie: Dict) -> None:
        """Reset health metrics for a cookie (useful after re-authentication)."""
        cookie_id = self._get_cookie_id(cookie)
        if cookie_id in self.health:
            self.health[cookie_id] = CookieHealth(cookie_id=cookie_id)
            logger.info(f"Reset health for cookie {cookie_id}")
    
    def _get_cookie_id(self, cookie: Dict) -> str:
        """Get unique identifier for cookie."""
        return cookie.get('id', cookie.get('name', str(id(cookie))))
    
    def _is_cookie_healthy(self, cookie: Dict) -> bool:
        """Check if cookie is healthy enough to use."""
        cookie_id = self._get_cookie_id(cookie)
        health = self.health.get(cookie_id)
        
        if not health:
            return True  # Unknown cookies are considered healthy
        
        return health.is_healthy


def demo():
    """Demo usage of smart cookie rotator."""
    # Sample cookies
    cookies = [
        {'id': 'cookie_1', 'name': 'Account 1'},
        {'id': 'cookie_2', 'name': 'Account 2'},
        {'id': 'cookie_3', 'name': 'Account 3'},
    ]
    
    rotator = SmartCookieRotator(cookies)
    
    # Simulate some usage
    for i in range(10):
        cookie = rotator.get_next_cookie()
        if cookie:
            # Random success/failure
            import random
            if random.random() > 0.2:
                rotator.record_success(cookie, watch_time=random.uniform(60, 300))
            else:
                rotator.record_failure(cookie, error="Timeout")
    
    # Show report
    print(rotator.get_health_report())
    print(f"\nHealthy cookies: {rotator.get_healthy_count()}/{len(cookies)}")


if __name__ == "__main__":
    demo()
