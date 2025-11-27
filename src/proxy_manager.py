import os
import random
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manage proxy rotation for scraping"""
    
    def __init__(self):
        self.use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        self.proxy_list = self._load_proxies()
        self.current_index = 0
    
    def _load_proxies(self) -> List[str]:
        """Load proxy list from environment or file"""
        proxies = []
        
        # From environment variable
        proxy_url = os.getenv('PROXY_URL')
        if proxy_url:
            proxies.append(proxy_url)
        
        # From file
        proxy_file = os.getenv('PROXY_FILE', 'proxies.txt')
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                proxies.extend([line.strip() for line in f if line.strip()])
        
        if proxies:
            logger.info(f"Loaded {len(proxies)} proxies")
        
        return proxies
    
    def get_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""
        if not self.use_proxy or not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return proxy
    
    def get_random_proxy(self) -> Optional[str]:
        """Get random proxy"""
        if not self.use_proxy or not self.proxy_list:
            return None
        
        return random.choice(self.proxy_list)
    
    def get_proxy_dict(self) -> Optional[dict]:
        """Get proxy as dict for requests"""
        proxy = self.get_proxy()
        if not proxy:
            return None
        
        return {
            'http': proxy,
            'https': proxy
        }
