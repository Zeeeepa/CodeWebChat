"""Session pool manager for browser automation"""

import time
from typing import Dict, Optional
from DrissionPage import ChromiumPage
from src.anti_detection import AntiDetection


class Session:
    """Wrapper for a browser session with lifecycle management"""
    
    def __init__(self, session_id: str, page: ChromiumPage):
        """Initialize session
        
        Args:
            session_id: Unique session identifier
            page: DrissionPage ChromiumPage instance
        """
        self.session_id = session_id
        self.page = page
        self.created_at = time.time()
        self.last_used = time.time()
        self.is_healthy = True
        self.provider = None  # Will be set when authenticated
    
    def touch(self) -> None:
        """Update last used timestamp"""
        self.last_used = time.time()
    
    def age(self) -> float:
        """Get session age in seconds
        
        Returns:
            Age in seconds since creation
        """
        return time.time() - self.created_at
    
    def idle_time(self) -> float:
        """Get idle time in seconds
        
        Returns:
            Seconds since last use
        """
        return time.time() - self.last_used


class SessionPool:
    """Manage pool of browser sessions with lifecycle and health monitoring"""
    
    def __init__(self, max_sessions: int = 10, max_age: int = 3600, ping_interval: int = 30):
        """Initialize session pool
        
        Args:
            max_sessions: Maximum concurrent sessions
            max_age: Maximum session age in seconds
            ping_interval: Health check interval in seconds
        """
        self.max_sessions = max_sessions
        self.max_age = max_age
        self.ping_interval = ping_interval
        self.sessions: Dict[str, Session] = {}
        self.anti_detection = AntiDetection()
    
    def allocate(self, provider: Optional[str] = None) -> Session:
        """Allocate a session from pool or create new one
        
        Args:
            provider: Optional provider name (e.g., 'z.ai', 'chatgpt')
        
        Returns:
            Session instance
            
        Raises:
            RuntimeError: If pool is exhausted
        """
        # Cleanup stale sessions first
        self._cleanup_stale()
        
        # Check pool size
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(
                f"Pool exhausted: {self.max_sessions} sessions active. "
                "Release sessions or increase max_sessions."
            )
        
        # Create new session with unique ID
        session_id = f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        # Create ChromiumPage instance
        page = ChromiumPage()
        
        # Apply anti-detection measures
        self.anti_detection.apply_to_page(page)
        
        # Create session wrapper
        session = Session(session_id, page)
        session.provider = provider
        
        # Add to pool
        self.sessions[session_id] = session
        
        return session
    
    def release(self, session_id: str) -> None:
        """Release a session back to pool and cleanup
        
        Args:
            session_id: Session ID to release
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            try:
                session.page.quit()
            except Exception:
                # Ignore errors during cleanup
                pass
            del self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session instance or None if not found
        """
        return self.sessions.get(session_id)
    
    def _cleanup_stale(self) -> None:
        """Remove stale sessions that exceeded max_age"""
        stale = []
        for session_id, session in self.sessions.items():
            if session.age() > self.max_age:
                stale.append(session_id)
        
        for session_id in stale:
            self.release(session_id)
    
    def health_check(self, session: Session) -> bool:
        """Perform health check on session
        
        Args:
            session: Session to check
            
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to get current URL as a simple health check
            _ = session.page.url
            return True
        except Exception:
            session.is_healthy = False
            return False
    
    def get_stats(self) -> dict:
        """Get pool statistics
        
        Returns:
            Dictionary with pool statistics
        """
        return {
            "total_sessions": len(self.sessions),
            "max_sessions": self.max_sessions,
            "utilization": len(self.sessions) / self.max_sessions if self.max_sessions > 0 else 0,
            "sessions": [
                {
                    "id": s.session_id,
                    "provider": s.provider,
                    "age": round(s.age(), 2),
                    "idle": round(s.idle_time(), 2),
                    "healthy": s.is_healthy,
                }
                for s in self.sessions.values()
            ]
        }
    
    def cleanup_all(self) -> None:
        """Cleanup all sessions in pool"""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            self.release(session_id)


# Add missing import
import random

