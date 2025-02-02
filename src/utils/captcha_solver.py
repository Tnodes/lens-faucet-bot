from typing import Optional
from twocaptcha import TwoCaptcha
import os
import time

class CaptchaSolver:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the captcha solver with 2captcha API key."""
        self.api_key = api_key or os.getenv('TWOCAPTCHA_API_KEY')
        if not self.api_key:
            raise ValueError("2captcha API key is required. Set TWOCAPTCHA_API_KEY environment variable or pass it directly.")
        
        self.solver = TwoCaptcha(self.api_key)

    def solve_turnstile(self, sitekey: str, url: str, retry_count: int = 3) -> Optional[str]:
        """
        Solve Cloudflare Turnstile captcha
        
        Args:
            sitekey: The sitekey from the Turnstile widget
            url: The URL where the captcha is located
            retry_count: Number of retries if solving fails
            
        Returns:
            The solved captcha token or None if failed
        """
        for attempt in range(retry_count):
            try:
                result = self.solver.turnstile(
                    sitekey=sitekey,
                    url=url
                )
                
                if result and 'code' in result:
                    return result['code']
                    
            except Exception as e:
                print(f"Attempt {attempt + 1}/{retry_count} failed: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(5)  # Wait before retry
                    
        return None 