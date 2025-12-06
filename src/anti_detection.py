"""Anti-detection module for browser fingerprinting and user-agent rotation"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List


class AntiDetection:
    """Manage browser fingerprints and user-agents for stealth"""
    
    def __init__(self):
        """Initialize with fingerprints and user agents"""
        self.fingerprints = self._load_fingerprints()
        self.user_agents = self._load_user_agents()
    
    def _load_fingerprints(self) -> List[Dict[str, Any]]:
        """Load chrome-fingerprints database
        
        Returns:
            List of fingerprint configurations
        """
        # Sample fingerprints (in production, load from chrome-fingerprints repo)
        return [
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "viewport": {"width": 1920, "height": 1080},
                "platform": "Win32",
                "languages": ["en-US", "en"],
                "hardwareConcurrency": 8,
                "deviceMemory": 8,
            },
            {
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "viewport": {"width": 1920, "height": 1080},
                "platform": "MacIntel",
                "languages": ["en-US", "en"],
                "hardwareConcurrency": 8,
                "deviceMemory": 16,
            },
            {
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "viewport": {"width": 1920, "height": 1080},
                "platform": "Linux x86_64",
                "languages": ["en-US", "en"],
                "hardwareConcurrency": 4,
                "deviceMemory": 8,
            },
        ]
    
    def _load_user_agents(self) -> List[str]:
        """Load UserAgent-Switcher patterns
        
        Returns:
            List of user agent strings
        """
        return [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Chrome Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ]
    
    def get_random_fingerprint(self) -> Dict[str, Any]:
        """Get a random fingerprint configuration
        
        Returns:
            Fingerprint dictionary with viewport, platform, etc.
        """
        return random.choice(self.fingerprints)
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string
        
        Returns:
            User agent string
        """
        return random.choice(self.user_agents)
    
    def apply_to_page(self, page) -> None:
        """Apply fingerprint and user-agent to DrissionPage instance
        
        Args:
            page: DrissionPage ChromiumPage instance
        """
        fp = self.get_random_fingerprint()
        ua = self.get_random_user_agent()
        
        # Set user agent
        page.set.user_agent(ua)
        
        # Set viewport size
        page.set.window.size(fp["viewport"]["width"], fp["viewport"]["height"])
        
        # Note: DrissionPage has native stealth built-in
        # Additional fingerprinting properties would be set via CDP
        # For MVP, user agent + viewport is sufficient

