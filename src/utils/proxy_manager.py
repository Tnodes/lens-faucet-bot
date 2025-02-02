from typing import Optional, Dict, List
import random
from datetime import datetime
from src.utils.logger import Logger


class ProxyManager:
    def __init__(self, proxy_file: str = "proxy.txt"):
        """Initialize the proxy manager."""
        self.proxy_file = proxy_file
        self.proxies: List[str] = []
        self.load_proxies()
        
    def load_proxies(self):
        """Load proxies from the proxy file."""
        try:
            with open(self.proxy_file, 'r') as f:
                # Skip empty lines and comments
                self.proxies = [
                    line.strip() 
                    for line in f.readlines() 
                    if line.strip() and not line.strip().startswith('#')
                ]
            Logger.info(f"Loaded {len(self.proxies)} proxies")
        except FileNotFoundError:
            Logger.warning(f"Warning: Proxy file {self.proxy_file} not found")
            self.proxies = []
            
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list."""
        if not self.proxies:
            return None
        proxy_url = random.choice(self.proxies)
        return self._format_proxy(proxy_url)
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in sequence."""
        if not self.proxies:
            return None
        
        # Rotate the proxy list
        proxy_url = self.proxies.pop(0)
        self.proxies.append(proxy_url)
        return self._format_proxy(proxy_url)
                
    def _format_proxy(self, proxy_url: str) -> Dict[str, str]:
        """Format proxy URL into the required dictionary format."""
        return {
            'http': f'http://{proxy_url}',
            'https': f'http://{proxy_url}'
        } 