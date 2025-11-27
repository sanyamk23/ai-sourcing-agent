"""
Browser Profile Manager - Reuse Chrome profile with saved LinkedIn cookies
"""
import os
import platform
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import logging

logger = logging.getLogger(__name__)


class BrowserProfileManager:
    """Manage Chrome profiles for persistent login sessions"""
    
    @staticmethod
    def get_chrome_profile_path():
        """Get the default Chrome profile path for the current OS"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif system == "Windows":
            return os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
        elif system == "Linux":
            return os.path.expanduser("~/.config/google-chrome")
        else:
            return None
    
    @staticmethod
    def create_driver_with_profile(profile_name: str = "Default", headless: bool = False):
        """
        Create Chrome driver using existing profile
        
        Args:
            profile_name: Chrome profile name (Default, Profile 1, Profile 2, etc.)
            headless: Whether to run in headless mode
        
        Returns:
            Chrome WebDriver with profile loaded
        """
        try:
            options = uc.ChromeOptions()
            
            # Get Chrome profile path
            profile_path = BrowserProfileManager.get_chrome_profile_path()
            
            if profile_path and os.path.exists(profile_path):
                # Use existing Chrome profile
                options.add_argument(f"--user-data-dir={profile_path}")
                options.add_argument(f"--profile-directory={profile_name}")
                logger.info(f"Using Chrome profile: {profile_path}/{profile_name}")
            else:
                logger.warning("Chrome profile not found, using temporary profile")
            
            # Additional options
            if headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Create driver
            driver = uc.Chrome(options=options)
            
            logger.info("Chrome driver created with profile")
            return driver
            
        except Exception as e:
            logger.error(f"Error creating driver with profile: {e}")
            # Fallback to regular driver
            return uc.Chrome()
    
    @staticmethod
    def create_custom_profile_driver(custom_profile_dir: str = "./chrome_profile", headless: bool = False):
        """
        Create Chrome driver with custom profile directory
        This creates a separate profile just for scraping
        
        Args:
            custom_profile_dir: Path to custom profile directory
            headless: Whether to run in headless mode
        
        Returns:
            Chrome WebDriver
        """
        try:
            options = uc.ChromeOptions()
            
            # Create custom profile directory if it doesn't exist
            os.makedirs(custom_profile_dir, exist_ok=True)
            
            # Use custom profile
            options.add_argument(f"--user-data-dir={custom_profile_dir}")
            
            if headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            driver = uc.Chrome(options=options)
            
            logger.info(f"Chrome driver created with custom profile: {custom_profile_dir}")
            return driver
            
        except Exception as e:
            logger.error(f"Error creating custom profile driver: {e}")
            return uc.Chrome()
    
    @staticmethod
    def list_chrome_profiles():
        """List available Chrome profiles"""
        profile_path = BrowserProfileManager.get_chrome_profile_path()
        
        if not profile_path or not os.path.exists(profile_path):
            logger.warning("Chrome profile directory not found")
            return []
        
        profiles = []
        
        # Check for Default profile
        if os.path.exists(os.path.join(profile_path, "Default")):
            profiles.append("Default")
        
        # Check for numbered profiles
        for i in range(1, 10):
            profile_name = f"Profile {i}"
            if os.path.exists(os.path.join(profile_path, profile_name)):
                profiles.append(profile_name)
        
        return profiles


def setup_linkedin_profile():
    """
    Interactive setup to login to LinkedIn once and save cookies
    Run this once to setup your profile
    """
    print("\n" + "="*60)
    print("  LinkedIn Profile Setup")
    print("="*60)
    print("\nThis will open Chrome and let you login to LinkedIn.")
    print("Your session will be saved for future use.")
    print("\nOptions:")
    print("1. Use your main Chrome profile (recommended)")
    print("2. Create a separate profile for scraping")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        # List available profiles
        profiles = BrowserProfileManager.list_chrome_profiles()
        
        if profiles:
            print("\nAvailable Chrome profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
            
            profile_choice = input(f"\nSelect profile (1-{len(profiles)}): ").strip()
            try:
                profile_name = profiles[int(profile_choice) - 1]
            except:
                profile_name = "Default"
        else:
            profile_name = "Default"
        
        print(f"\nUsing profile: {profile_name}")
        driver = BrowserProfileManager.create_driver_with_profile(profile_name, headless=False)
    else:
        print("\nCreating custom profile for scraping...")
        driver = BrowserProfileManager.create_custom_profile_driver("./chrome_profile_linkedin", headless=False)
    
    try:
        print("\n" + "="*60)
        print("  Opening LinkedIn...")
        print("="*60)
        print("\n1. A Chrome window will open")
        print("2. Login to LinkedIn if not already logged in")
        print("3. Once logged in, press Enter here")
        print("\n" + "="*60)
        
        driver.get("https://www.linkedin.com")
        
        input("\nPress Enter after you've logged in to LinkedIn...")
        
        # Verify login
        if "feed" in driver.current_url or "mynetwork" in driver.current_url:
            print("\n✅ Successfully logged in!")
            print("Your session is now saved.")
            print("\nYou can now use the scraper without logging in again.")
        else:
            print("\n⚠️  Login verification unclear. Please check manually.")
        
        driver.quit()
        
        print("\n" + "="*60)
        print("  Setup Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Update your config to use the profile")
        print("2. Run your scraper - it will use saved cookies")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        driver.quit()


if __name__ == "__main__":
    # Run setup
    setup_linkedin_profile()
