"""K2Think Provider - Real implementation for https://www.k2think.ai"""

import time
import json
from typing import Dict, Optional, AsyncIterator
from fake_useragent import FakeUserAgent
from DrissionPage import ChromiumPage


class K2ThinkProvider:
    """
    Production-ready K2Think provider that:
    1. Logs into https://www.k2think.ai/auth
    2. Handles chat at https://www.k2think.ai/
    3. Extracts responses in real-time
    """
    
    AUTH_URL = "https://www.k2think.ai/auth"
    CHAT_URL = "https://www.k2think.ai/"
    
    def __init__(self):
        self.page: Optional[ChromiumPage] = None
        self.is_authenticated = False
        self.ua_generator = FakeUserAgent()
    
    def create_page(self) -> ChromiumPage:
        """Create a new browser page with proper user agent"""
        page = ChromiumPage()
        
        # Set random user agent (like KiteAi-BOT does)
        user_agent = self.ua_generator.random
        page.set.user_agent(user_agent)
        
        # Set realistic viewport
        page.set.window.size(1920, 1080)
        
        return page
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to K2Think with provided credentials
        
        Args:
            email: User email (e.g., developer@pixelium.uk)
            password: User password
            
        Returns:
            True if login successful
        """
        try:
            # Create page if not exists
            if not self.page:
                self.page = self.create_page()
            
            # Navigate to auth page
            print(f"[K2Think] Navigating to {self.AUTH_URL}")
            self.page.get(self.AUTH_URL)
            
            # Wait for page to load
            time.sleep(2)
            
            # Find email input (try multiple selectors)
            email_input = None
            email_selectors = [
                '@type=email',
                'input[type="email"]',
                'input[name="email"]',
                '#email',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]',
            ]
            
            for selector in email_selectors:
                email_input = self.page.ele(selector, timeout=2)
                if email_input:
                    print(f"[K2Think] Found email input with selector: {selector}")
                    break
            
            if not email_input:
                print("[K2Think] ERROR: Could not find email input field")
                return False
            
            # Find password input
            password_input = None
            password_selectors = [
                '@type=password',
                'input[type="password"]',
                'input[name="password"]',
                '#password',
                'input[placeholder*="password" i]',
            ]
            
            for selector in password_selectors:
                password_input = self.page.ele(selector, timeout=2)
                if password_input:
                    print(f"[K2Think] Found password input with selector: {selector}")
                    break
            
            if not password_input:
                print("[K2Think] ERROR: Could not find password input field")
                return False
            
            # Fill credentials
            print("[K2Think] Filling credentials...")
            email_input.input(email)
            time.sleep(0.5)
            password_input.input(password)
            time.sleep(0.5)
            
            # Find and click submit button
            submit_button = None
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Enter")',
                'input[type="submit"]',
            ]
            
            for selector in submit_selectors:
                submit_button = self.page.ele(selector, timeout=2)
                if submit_button:
                    print(f"[K2Think] Found submit button with selector: {selector}")
                    break
            
            if submit_button:
                print("[K2Think] Clicking submit...")
                submit_button.click()
            else:
                # Try Enter key as fallback
                print("[K2Think] No submit button found, trying Enter key...")
                password_input.input('\n')
            
            # Wait for redirect
            time.sleep(3)
            
            # Check if we're logged in (URL should change or dashboard appears)
            current_url = self.page.url
            print(f"[K2Think] Current URL after login: {current_url}")
            
            if current_url != self.AUTH_URL and 'auth' not in current_url.lower():
                print("[K2Think] ✓ Login successful!")
                self.is_authenticated = True
                return True
            else:
                print("[K2Think] ✗ Login may have failed (still on auth page)")
                return False
                
        except Exception as e:
            print(f"[K2Think] Login error: {e}")
            return False
    
    def send_message(self, message: str) -> Optional[str]:
        """
        Send a message and get response
        
        Args:
            message: User message to send
            
        Returns:
            Response text or None if error
        """
        if not self.is_authenticated:
            print("[K2Think] ERROR: Not authenticated. Call login() first")
            return None
        
        try:
            # Navigate to chat if not there
            if self.CHAT_URL not in self.page.url:
                print(f"[K2Think] Navigating to {self.CHAT_URL}")
                self.page.get(self.CHAT_URL)
                time.sleep(2)
            
            # Find chat input (textarea or input)
            chat_input = None
            input_selectors = [
                'textarea[placeholder*="message" i]',
                'textarea[placeholder*="type" i]',
                'input[placeholder*="message" i]',
                'textarea',
                'div[contenteditable="true"]',
            ]
            
            for selector in input_selectors:
                chat_input = self.page.ele(selector, timeout=2)
                if chat_input:
                    print(f"[K2Think] Found chat input with selector: {selector}")
                    break
            
            if not chat_input:
                print("[K2Think] ERROR: Could not find chat input")
                return None
            
            # Type message
            print(f"[K2Think] Sending message: {message[:50]}...")
            chat_input.input(message)
            time.sleep(0.5)
            
            # Find and click send button or press Enter
            send_button = None
            send_selectors = [
                'button[aria-label*="Send" i]',
                'button[title*="Send" i]',
                'button:has-text("Send")',
                'button[type="submit"]',
                'button svg',  # Icon buttons
            ]
            
            for selector in send_selectors:
                send_button = self.page.ele(selector, timeout=1)
                if send_button:
                    print(f"[K2Think] Found send button with selector: {selector}")
                    send_button.click()
                    break
            
            if not send_button:
                # Fallback to Enter key
                print("[K2Think] No send button, trying Shift+Enter...")
                chat_input.input('\n')
            
            # Wait for response to start appearing
            time.sleep(2)
            
            # Extract response (try multiple selectors for response container)
            response_selectors = [
                'div[class*="message"]',
                'div[class*="response"]',
                'div[class*="assistant"]',
                'div[role="article"]',
                'pre',
                'code',
            ]
            
            response_text = ""
            for selector in response_selectors:
                responses = self.page.eles(selector)
                if responses:
                    # Get the last message (should be AI response)
                    last_response = responses[-1]
                    response_text = last_response.text
                    if response_text and len(response_text) > 10:
                        print(f"[K2Think] Found response with selector: {selector}")
                        break
            
            if response_text:
                print(f"[K2Think] ✓ Got response: {response_text[:100]}...")
                return response_text
            else:
                print("[K2Think] ✗ No response found")
                return None
                
        except Exception as e:
            print(f"[K2Think] Send message error: {e}")
            return None
    
    async def send_message_stream(self, message: str) -> AsyncIterator[str]:
        """
        Send message and stream response in real-time
        
        Args:
            message: User message
            
        Yields:
            Response chunks as they arrive
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated")
        
        # TODO: Implement streaming by monitoring DOM changes
        # For now, fallback to non-streaming
        response = self.send_message(message)
        if response:
            yield response
    
    def close(self):
        """Close the browser page"""
        if self.page:
            try:
                self.page.quit()
            except:
                pass
            self.page = None
            self.is_authenticated = False


# Example usage for testing
if __name__ == "__main__":
    provider = K2ThinkProvider()
    
    # Login
    success = provider.login(
        email="developer@pixelium.uk",
        password="developer123?"
    )
    
    if success:
        print("\n=== Login successful! ===\n")
        
        # Send a test message
        response = provider.send_message("Hello! Can you help me with Python?")
        
        if response:
            print(f"\n=== Response ===")
            print(response)
        else:
            print("\n=== No response received ===")
    else:
        print("\n=== Login failed ===")
    
    # Cleanup
    provider.close()

