#!/usr/bin/env python3
"""
Naukri Persistent Browser Manager
Manages a single persistent Chrome browser instance for Naukri Resdex
"""

import os
import time
import undetected_chromedriver as uc
from pathlib import Path

class PersistentBrowser:
    """Base class for persistent browser instances"""
    
    def __init__(self, profile_dir, portal_name):
        self._driver = None
        self._is_logged_in = False
        self._profile_dir = profile_dir
        self._portal_name = portal_name
    
    def get_driver(self):
        """Get or create the persistent browser"""
        if self._driver is None:
            print(f"🌐 Creating persistent {self._portal_name} browser with saved profile...")
            
            # Create profile directory if it doesn't exist
            Path(self._profile_dir).mkdir(exist_ok=True)
            
            # Configure Chrome with persistent profile
            options = uc.ChromeOptions()
            options.add_argument(f'--user-data-dir={os.path.abspath(self._profile_dir)}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--profile-directory=Default')
            
            # Create driver
            self._driver = uc.Chrome(options=options)
            print(f"✅ {self._portal_name} browser created with persistent profile")
        else:
            print(f"♻️  Reusing existing {self._portal_name} browser session")
        
        return self._driver
    
    def is_logged_in(self):
        """Check if logged in"""
        return self._is_logged_in
    
    def set_logged_in(self, status=True):
        """Mark as logged in"""
        self._is_logged_in = status
    
    def close(self):
        """Close the browser (use sparingly!)"""
        if self._driver:
            print(f"🔒 Closing {self._portal_name} browser...")
            try:
                self._driver.quit()
            except:
                pass
            self._driver = None
            self._is_logged_in = False
            print(f"✅ {self._portal_name} browser closed")
    
    def check_login_status(self):
        """Check if we're still logged in"""
        if self._driver:
            try:
                current_url = self._driver.current_url
                if "login" in current_url.lower() or "signin" in current_url.lower():
                    self._is_logged_in = False
                    return False
                else:
                    self._is_logged_in = True
                    return True
            except:
                pass
        return self._is_logged_in

class NaukriPersistentBrowser(PersistentBrowser):
    """Singleton browser instance for Naukri Resdex"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not NaukriPersistentBrowser._initialized:
            super().__init__("./chrome_profile_naukri", "Naukri")
            NaukriPersistentBrowser._initialized = True
    
    def navigate_to_requirement(self, requirement_id):
        """Navigate to a specific requirement"""
        driver = self.get_driver()
        url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={requirement_id}&requirementGroupId={requirement_id}&resPerPage=50&pageNo=1&activeTab=potential"
        print(f"📍 Navigating to requirement: {requirement_id}")
        driver.get(url)
        return driver

class LinkedInPersistentBrowser(PersistentBrowser):
    """Singleton browser instance for LinkedIn"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LinkedInPersistentBrowser._initialized:
            super().__init__("./chrome_profile_linkedin", "LinkedIn")
            LinkedInPersistentBrowser._initialized = True
    
    def navigate_to_search(self, keywords, location=""):
        """Navigate to LinkedIn people search"""
        driver = self.get_driver()
        from urllib.parse import quote_plus
        url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(keywords)}"
        if location:
            url += f"&location={quote_plus(location)}"
        print(f"📍 Navigating to LinkedIn search: {keywords}")
        driver.get(url)
        return driver

# Global instances
naukri_browser_manager = NaukriPersistentBrowser()
linkedin_browser_manager = LinkedInPersistentBrowser()

# Backward compatibility
browser_manager = naukri_browser_manager
