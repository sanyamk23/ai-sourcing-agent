import asyncio
import aiohttp
import ssl
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.models import Candidate, JobDescription
import logging
import hashlib
import time
import re
import os
from urllib.parse import quote_plus, urlencode

import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

class BasePortalScraper:
    """Base class for job portal scrapers"""
    
    def __init__(self, portal_name: str, base_url: str, config: dict):
        self.portal_name = portal_name
        self.base_url = base_url
        self.config = config
        self.max_candidates = config['scraping']['max_candidates_per_portal']
        self.timeout = config['scraping']['timeout_seconds']
        self.rate_limit_delay = config['scraping'].get('rate_limit_delay', 2)
    
    def _get_driver(self, headless: bool = True, use_profile: bool = False):
        """Create Selenium WebDriver with anti-detection and optional profile"""
        if use_profile and not headless:
            # Use saved Chrome profile with LinkedIn cookies
            try:
                from src.browser_profile_manager import BrowserProfileManager
                driver = BrowserProfileManager.create_custom_profile_driver(
                    "./chrome_profile_linkedin",
                    headless=False
                )
                logger.info("Using Chrome profile with saved session")
                return driver
            except Exception as e:
                logger.warning(f"Could not load profile: {e}")
        
        # Regular driver
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        driver = uc.Chrome(options=options)
        return driver
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        """Override in subclass"""
        raise NotImplementedError

class LinkedInScraper(BasePortalScraper):
    """Real LinkedIn scraper using Selenium (most reliable)"""
    
    # Class-level shared browser instance
    _shared_driver = None
    _is_logged_in = False
    
    def __init__(self, portal_name: str, base_url: str, config: dict):
        super().__init__(portal_name, base_url, config)
        self.linkedin_username = os.getenv('LINKEDIN_USERNAME')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        
        # Try to import persistent browser manager
        try:
            from naukri_persistent_browser import linkedin_browser_manager
            self.browser_manager = linkedin_browser_manager
        except:
            self.browser_manager = None
    
    def _get_or_create_driver(self):
        """Get existing driver or create a new one"""
        if LinkedInScraper._shared_driver is None:
            logger.info("Creating new persistent browser session...")
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            # Keep browser open between sessions
            options.add_experimental_option("detach", True)
            
            LinkedInScraper._shared_driver = uc.Chrome(options=options)
            logger.info("✓ Persistent browser created")
        else:
            logger.info("♻️  Reusing existing browser session")
        
        return LinkedInScraper._shared_driver
    
    @classmethod
    def close_browser(cls):
        """Manually close the persistent browser session"""
        if cls._shared_driver:
            logger.info("Closing persistent browser session...")
            cls._shared_driver.quit()
            cls._shared_driver = None
            cls._is_logged_in = False
            logger.info("✓ Browser closed")
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        """Scrape LinkedIn for candidates"""
        logger.info(f"Scraping LinkedIn for: {job_description.title}")
        
        # Use Selenium as primary method (most reliable)
        return await self._scrape_with_selenium(job_description)
    

    
    async def _scrape_with_selenium(self, job_description: JobDescription) -> List[Candidate]:
        """Scrape LinkedIn with Selenium - optimized for people search"""
        candidates = []
        driver = None
        start_time = time.time()
        max_duration = 60  # Maximum 60 seconds for LinkedIn scraping
        
        try:
            # Try persistent browser first
            if self.browser_manager:
                try:
                    logger.info("♻️  Using persistent LinkedIn browser")
                    driver = self.browser_manager.get_driver()
                    # Mark as logged in if we got the driver
                    if driver:
                        self.browser_manager.set_logged_in(True)
                except Exception as e:
                    logger.warning(f"Could not use persistent browser: {e}")
                    import traceback
                    traceback.print_exc()
                    driver = None
            
            # Fallback to profile-based driver
            if not driver:
                logger.info("Using Chrome profile with saved session")
                driver = self._get_driver(headless=False, use_profile=True)
            
            # Check if already logged in (from saved cookies)
            logger.info("Checking LinkedIn login status...")
            driver.get("https://www.linkedin.com/feed")
            await asyncio.sleep(3)
            
            # If already logged in, skip login
            if "feed" in driver.current_url or "mynetwork" in driver.current_url:
                logger.info("✅ Already logged in to LinkedIn (using saved cookies)")
            else:
                # Need to login
                logger.info("Not logged in, attempting login...")
                
                if not self.linkedin_username or not self.linkedin_password:
                    logger.error("LinkedIn credentials not provided in .env file")
                    return candidates
                
                try:
                    driver.get("https://www.linkedin.com/login")
                    await asyncio.sleep(3)
                    
                    # Enter credentials
                    username_field = driver.find_element(By.ID, "username")
                    password_field = driver.find_element(By.ID, "password")
                    
                    username_field.send_keys(self.linkedin_username)
                    await asyncio.sleep(1)
                    password_field.send_keys(self.linkedin_password)
                    await asyncio.sleep(1)
                    
                    # Click login
                    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                    await asyncio.sleep(5)
                    
                    # Check if login successful
                    if "feed" in driver.current_url or "mynetwork" in driver.current_url:
                        logger.info("✓ LinkedIn login successful")
                    else:
                        logger.warning("LinkedIn login may have failed - check for CAPTCHA")
                        await asyncio.sleep(10)  # Give time to solve CAPTCHA manually
                    
                except Exception as e:
                    logger.error(f"LinkedIn login error: {e}")
                    return candidates
            
            # Search for people with relevant skills
            logger.info(f"Searching LinkedIn for: {job_description.title}")
            
            # Build people search URL directly
            keywords = quote_plus(job_description.title)
            location = quote_plus(job_description.location) if job_description.location else ""
            
            # Use LinkedIn's people search URL
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            if location:
                search_url += f"&location={location}"
            
            logger.info(f"Navigating to: {search_url}")
            
            # Navigate directly to search results
            driver.get(search_url)
            await asyncio.sleep(5)  # Wait for results to load
            
            logger.info(f"Current URL: {driver.current_url}")
            
            # Scroll to load more results
            logger.info("Scrolling to load more results...")
            for i in range(3):
                # Check timeout
                if time.time() - start_time > max_duration:
                    logger.warning(f"⏱️  LinkedIn scraping timeout ({max_duration}s) - moving on")
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                logger.info(f"Scroll {i+1}/3 complete")
            
            # Find all profile cards - try multiple selectors
            profile_cards = []
            selectors_to_try = [
                "li.reusable-search__result-container",  # New LinkedIn structure
                "[data-chameleon-result-urn]",  # Old structure
                "div.entity-result",  # Alternative
                "li[class*='search-result']",  # Fallback
            ]
            
            for selector in selectors_to_try:
                try:
                    profile_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(profile_cards) > 0:
                        logger.info(f"Found {len(profile_cards)} profile cards using selector: {selector}")
                        break
                except:
                    continue
            
            if not profile_cards:
                logger.warning("⚠️  No profile cards found with any selector")
                logger.info("💾 Saving page source for debugging...")
                with open("linkedin_page_debug.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("   Saved to: linkedin_page_debug.html")
            
            for i, card in enumerate(profile_cards[:self.max_candidates]):
                # Check timeout
                if time.time() - start_time > max_duration:
                    logger.warning(f"⏱️  LinkedIn scraping timeout - extracted {len(candidates)} candidates")
                    break
                
                try:
                    # Extract name - try multiple selectors
                    name = "LinkedIn User"
                    name_selectors = [
                        "span.entity-result__title-text a span[aria-hidden='true']",  # New structure
                        ".entity-result__title-text span[aria-hidden='true']",
                        "a.app-aware-link span[aria-hidden='true']",
                        "span[dir='ltr'] span[aria-hidden='true']",
                        ".entity-result__title-text span",
                        "a span[dir='ltr']",
                    ]
                    for name_selector in name_selectors:
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, name_selector)
                            name_text = name_elem.text.strip()
                            if name_text and len(name_text) > 2 and not name_text.startswith("View"):
                                name = name_text
                                break
                        except:
                            continue
                    
                    # Extract title/headline - try multiple selectors
                    title = job_description.title
                    for title_selector in [
                        ".entity-result__primary-subtitle",
                        "[class*='primary-subtitle']",
                        "div[class*='subtitle'] div:first-child"
                    ]:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, title_selector)
                            title_text = title_elem.text.strip()
                            if title_text:
                                title = title_text
                                break
                        except:
                            continue
                    
                    # Extract location - try multiple selectors
                    location = job_description.location or ""
                    for loc_selector in [
                        ".entity-result__secondary-subtitle",
                        "[class*='secondary-subtitle']",
                        "div[class*='subtitle'] div:nth-child(2)"
                    ]:
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, loc_selector)
                            loc_text = location_elem.text.strip()
                            if loc_text:
                                location = loc_text
                                break
                        except:
                            continue
                    
                    # Extract profile URL
                    profile_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
                    try:
                        profile_link = card.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
                        profile_url = profile_link.get_attribute("href")
                        # Clean URL
                        if "?" in profile_url:
                            profile_url = profile_url.split("?")[0]
                    except:
                        pass
                    
                    # Extract profile ID for unique identification
                    profile_id = profile_url.split("/in/")[-1].rstrip("/") if "/in/" in profile_url else f"user_{i}"
                    
                    # Create candidate
                    candidate = Candidate(
                        id=hashlib.md5(f"linkedin_{profile_id}".encode()).hexdigest(),
                        name=name,
                        current_title=title,
                        skills=job_description.required_skills,  # Assume they have the skills we're searching for
                        location=location,
                        profile_url=profile_url,
                        source_portal="linkedin",
                        summary=f"Found via LinkedIn search for: {job_description.title}"
                    )
                    
                    candidates.append(candidate)
                    logger.info(f"  {i+1}. {name} - {title}")
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error extracting profile {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
        finally:
            # TEMPORARY: Keep browser open for debugging
            if driver:
                logger.info("💡 Keeping LinkedIn browser open for debugging - close manually")
                # try:
                #     logger.info("🔒 Closing LinkedIn browser...")
                #     driver.quit()
                # except:
                #     pass
        
        logger.info(f"✓ Found {len(candidates)} candidates from LinkedIn")
        return candidates

class IndeedScraper(BasePortalScraper):
    """Real Indeed scraper"""
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        logger.info(f"Scraping Indeed for: {job_description.title}")
        candidates = []
        driver = None
        
        try:
            driver = self._get_driver(headless=self.config['scraping'].get('headless', True))
            
            # Build search URL
            params = {
                'q': job_description.title,
                'l': job_description.location or '',
                'limit': 50
            }
            search_url = f"https://www.indeed.com/jobs?{urlencode(params)}"
            
            driver.get(search_url)
            await asyncio.sleep(3)
            
            # Find job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon, .jobsearch-SerpJobCard")
            
            for i, card in enumerate(job_cards[:self.max_candidates]):
                try:
                    # Extract job details
                    title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle, .jobTitle").text
                    company = card.find_element(By.CSS_SELECTOR, ".companyName").text
                    location = card.find_element(By.CSS_SELECTOR, ".companyLocation").text
                    
                    # Try to get job description
                    try:
                        card.click()
                        await asyncio.sleep(1)
                        description_elem = driver.find_element(By.ID, "jobDescriptionText")
                        description = description_elem.text
                    except:
                        description = ""
                    
                    # Extract skills from description
                    skills = []
                    for skill in job_description.required_skills:
                        if skill.lower() in description.lower():
                            skills.append(skill)
                    
                    # Try to get job URL
                    try:
                        job_link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    except:
                        job_link = search_url
                    
                    candidate = Candidate(
                        id=hashlib.md5(f"indeed_{i}_{title}_{company}".encode()).hexdigest(),
                        name=f"Candidate at {company}",
                        current_title=title,
                        skills=skills or job_description.required_skills[:2],
                        location=location,
                        profile_url=job_link,
                        source_portal="indeed",
                        summary=description[:200] if description else None
                    )
                    candidates.append(candidate)
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error extracting Indeed job: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        finally:
            if driver:
                driver.quit()
        
        logger.info(f"Found {len(candidates)} candidates from Indeed")
        return candidates

class GlassdoorScraper(BasePortalScraper):
    """Real Glassdoor scraper"""
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        logger.info(f"Scraping Glassdoor for: {job_description.title}")
        candidates = []
        driver = None
        
        try:
            driver = self._get_driver(headless=self.config['scraping'].get('headless', True))
            
            # Build search URL
            keywords = quote_plus(job_description.title)
            location = quote_plus(job_description.location or '')
            search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords}&locT=&locId=&jobType="
            
            driver.get(search_url)
            await asyncio.sleep(4)
            
            # Find job listings
            job_cards = driver.find_elements(By.CSS_SELECTOR, "li.react-job-listing, .JobsList_jobListItem__wjTHv")
            
            for i, card in enumerate(job_cards[:self.max_candidates]):
                try:
                    # Click to view details
                    card.click()
                    await asyncio.sleep(2)
                    
                    # Extract details
                    title = driver.find_element(By.CSS_SELECTOR, "[data-test='job-title'], .JobDetails_jobTitle__Rw_gn").text
                    company = driver.find_element(By.CSS_SELECTOR, "[data-test='employer-name'], .EmployerProfile_employerName__Xemli").text
                    location = driver.find_element(By.CSS_SELECTOR, "[data-test='location'], .JobDetails_location__mSg5h").text
                    
                    # Get description
                    try:
                        description = driver.find_element(By.CSS_SELECTOR, "[data-test='jobDescriptionText'], .JobDetails_jobDescription__uW_fK").text
                    except:
                        description = ""
                    
                    # Extract skills
                    skills = []
                    for skill in job_description.required_skills:
                        if skill.lower() in description.lower():
                            skills.append(skill)
                    
                    candidate = Candidate(
                        id=hashlib.md5(f"glassdoor_{i}_{title}_{company}".encode()).hexdigest(),
                        name=f"Professional at {company}",
                        current_title=title,
                        skills=skills or job_description.required_skills[:3],
                        location=location,
                        profile_url=driver.current_url,
                        source_portal="glassdoor",
                        summary=description[:200] if description else None
                    )
                    candidates.append(candidate)
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error extracting Glassdoor job: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Glassdoor scraping error: {e}")
        finally:
            if driver:
                driver.quit()
        
        logger.info(f"Found {len(candidates)} candidates from Glassdoor")
        return candidates

class GitHubJobsScraper(BasePortalScraper):
    """Scrape GitHub for developer profiles"""
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        logger.info(f"Scraping GitHub for: {job_description.title}")
        candidates = []
        
        try:
            # Create SSL context that doesn't verify certificates (for development)
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Search for users with relevant skills
                for skill in job_description.required_skills[:3]:
                    search_url = f"https://api.github.com/search/users?q={quote_plus(skill)}+type:user&per_page=30"
                    
                    async with session.get(search_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for user in data.get('items', [])[:20]:
                                try:
                                    # Get user details
                                    user_url = user['url']
                                    async with session.get(user_url) as user_response:
                                        if user_response.status == 200:
                                            user_data = await user_response.json()
                                            
                                            # Ensure name is not None
                                            name = user_data.get('name') or user_data.get('login') or 'GitHub User'
                                            
                                            candidate = Candidate(
                                                id=hashlib.md5(f"github_{user_data['login']}".encode()).hexdigest(),
                                                name=name,
                                                email=user_data.get('email'),
                                                current_title=user_data.get('bio') or 'Developer',
                                                skills=[skill],
                                                location=user_data.get('location') or '',
                                                profile_url=user_data['html_url'],
                                                source_portal="github",
                                                summary=f"GitHub: {user_data.get('public_repos', 0)} repos, {user_data.get('followers', 0)} followers"
                                            )
                                            candidates.append(candidate)
                                    
                                    await asyncio.sleep(1)  # Rate limiting
                                    
                                except Exception as e:
                                    logger.error(f"Error fetching GitHub user: {e}")
                                    continue
                    
                    await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"GitHub scraping error: {e}")
        
        logger.info(f"Found {len(candidates)} candidates from GitHub")
        return candidates

class StackOverflowScraper(BasePortalScraper):
    """Scrape StackOverflow for developer profiles"""
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        logger.info(f"Scraping StackOverflow for: {job_description.title}")
        candidates = []
        
        try:
            # Create SSL context that doesn't verify certificates (for development)
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Use StackExchange API
                for skill in job_description.required_skills[:3]:
                    api_url = f"https://api.stackexchange.com/2.3/users?order=desc&sort=reputation&inname={quote_plus(skill)}&site=stackoverflow&pagesize=30"
                    
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for user in data.get('items', [])[:20]:
                                candidate = Candidate(
                                    id=hashlib.md5(f"stackoverflow_{user['user_id']}".encode()).hexdigest(),
                                    name=user.get('display_name', 'Anonymous'),
                                    current_title=f"Developer (Reputation: {user.get('reputation', 0)})",
                                    skills=[skill],
                                    location=user.get('location', ''),
                                    profile_url=user.get('link', ''),
                                    source_portal="stackoverflow",
                                    summary=f"Reputation: {user.get('reputation', 0)}, Badges: {user.get('badge_counts', {}).get('gold', 0)} gold"
                                )
                                candidates.append(candidate)
                            
                            await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"StackOverflow scraping error: {e}")
        
        logger.info(f"Found {len(candidates)} candidates from StackOverflow")
        return candidates

class NaukriScraper(BasePortalScraper):
    """Scrape Naukri Resdex (Recruiter platform) for candidates"""
    
    # Class-level shared browser instance
    _shared_driver = None
    _is_logged_in = False
    
    def __init__(self, portal_name: str, base_url: str, config: dict):
        super().__init__(portal_name, base_url, config)
        self.resdex_cookies = os.getenv('NAUKRI_RESDEX_COOKIES', '')
        self.requirement_id = os.getenv('NAUKRI_REQUIREMENT_ID', '125289')
        
        # Try to import persistent browser manager
        try:
            from naukri_persistent_browser import browser_manager
            self.browser_manager = browser_manager
        except:
            self.browser_manager = None
    
    @classmethod
    def set_shared_driver(cls, driver):
        """Set a shared browser instance (called from setup script)"""
        cls._shared_driver = driver
        cls._is_logged_in = True
        logger.info("✅ Shared browser session configured")
    
    @classmethod
    def close_browser(cls):
        """Manually close the persistent browser session"""
        if cls._shared_driver:
            logger.info("Closing persistent Naukri Resdex browser session...")
            try:
                cls._shared_driver.quit()
            except:
                pass
            cls._shared_driver = None
            cls._is_logged_in = False
            logger.info("✓ Naukri Resdex browser closed")
    
    async def scrape(self, job_description: JobDescription) -> List[Candidate]:
        """Scrape Naukri Resdex for candidates"""
        logger.info(f"🔍 Scraping Naukri Resdex for: {job_description.title}")
        candidates = []
        driver = None
        should_close_driver = False
        
        # Try persistent browser manager first
        if self.browser_manager:
            try:
                logger.info("♻️  Using persistent browser manager")
                driver = self.browser_manager.get_driver()
                should_close_driver = False
                self.browser_manager.set_logged_in(True)
                
                # Navigate to requirement
                requirement_url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={self.requirement_id}&requirementGroupId={self.requirement_id}&resPerPage=50&pageNo=1&activeTab=potential"
                logger.info(f"📍 Navigating to requirement: {self.requirement_id}")
                driver.get(requirement_url)
                await asyncio.sleep(3)
                
                # Successfully using persistent browser, skip cookie setup
                logger.info("✅ Using persistent browser session")
                
            except Exception as e:
                logger.warning(f"Could not use persistent browser: {e}")
                import traceback
                traceback.print_exc()
                # Fall through to cookie-based method
                self.browser_manager = None
                driver = None
        
        # Check if we have a shared browser session (fallback)
        if not driver and NaukriScraper._shared_driver and NaukriScraper._is_logged_in:
            logger.info("♻️  Reusing existing browser session")
            driver = NaukriScraper._shared_driver
            should_close_driver = False
        
        # If no persistent browser, create new one with cookies
        if not driver:
            # Check configuration for cookie-based login
            if not self.resdex_cookies or self.resdex_cookies == 'your_cookies_here':
                logger.error("❌ NAUKRI_RESDEX_COOKIES not configured!")
                logger.info("   Run: python3 setup_naukri_cookies.py")
                return candidates
            
            if not self.requirement_id:
                logger.error("❌ NAUKRI_REQUIREMENT_ID not configured!")
                logger.info("   Set NAUKRI_REQUIREMENT_ID in .env")
                return candidates
            
            # Create new browser with cookies
            logger.info("🌐 Opening new browser with cookies...")
            driver = self._get_driver(headless=False)
            should_close_driver = True
            
            # Navigate to Resdex first
            logger.info("📍 Loading Resdex...")
            driver.get("https://resdex.naukri.com/lite")
            await asyncio.sleep(2)
            
            # Add cookies - strip quotes from cookie string
            logger.info("🍪 Adding authentication cookies...")
            cookie_string = self.resdex_cookies.strip().strip("'").strip('"')
            cookie_pairs = cookie_string.split(';')
            cookies_added = 0
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    try:
                        driver.add_cookie({
                            'name': name.strip(),
                            'value': value.strip(),
                            'domain': '.naukri.com'
                        })
                        cookies_added += 1
                    except Exception as e:
                        logger.debug(f"Could not add cookie {name}: {e}")
            
            logger.info(f"✅ Added {cookies_added} cookies")
            
            # Navigate to requirement
            search_url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={self.requirement_id}&requirementGroupId={self.requirement_id}&resPerPage=50&pageNo=1&activeTab=potential"
            logger.info(f"📍 Opening requirement: {self.requirement_id}")
            driver.get(search_url)
            await asyncio.sleep(5)
        
        try:
            
            # Define search_url for use in extraction
            search_url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={self.requirement_id}&requirementGroupId={self.requirement_id}&resPerPage=50&pageNo=1&activeTab=potential"
            
            # Check if we're logged in
            current_url = driver.current_url
            if "login" in current_url.lower() or "signin" in current_url.lower():
                if should_close_driver:
                    logger.error("❌ Cookies expired or invalid!")
                    logger.info("   Run: python3 setup_naukri_cookies.py to get fresh cookies")
                else:
                    logger.error("❌ Session expired!")
                    logger.info("   Please re-run: python3 setup_naukri_cookies.py")
                    NaukriScraper._is_logged_in = False
                return candidates
            
            logger.info(f"✅ Logged in successfully")
            logger.info(f"📄 Current page: {driver.title}")
            
            # Determine how many pages to scrape
            max_pages = 2  # Scrape 2 pages = 100 candidates (50 per page)
            all_candidates = []
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"📄 Scraping page {page_num}/{max_pages}...")
                
                # Navigate to specific page
                page_url = f"{search_url}&pageNo={page_num}"
                if page_num > 1:
                    driver.get(page_url)
                    await asyncio.sleep(3)
                
                # Scroll to load all candidates on this page
                logger.info("📜 Scrolling to load candidates...")
                for i in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(1)
            
                # Wait for React app to load
                logger.info("⏳ Waiting for page to load...")
                await asyncio.sleep(2)
                
                # Find candidate cards - look for the actual structure
                logger.info("🔍 Looking for candidate cards...")
                candidate_elements = []
            
                # Try to find the candidate profile summary links (these contain the data)
                try:
                    candidate_elements = driver.find_elements(By.CSS_SELECTOR, "a.candidate-profile-summary")
                    if candidate_elements:
                        logger.info(f"✅ Found {len(candidate_elements)} candidates using profile summary selector")
                except:
                    pass
                
                # Fallback: try other selectors
                if not candidate_elements:
                    resdex_selectors = [
                        "div[class*='candidate']",
                        "div[class*='Card']",
                        "article"
                    ]
                    
                    for selector in resdex_selectors:
                        try:
                            candidate_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(candidate_elements) > 5:
                                logger.info(f"✅ Found {len(candidate_elements)} elements with selector: {selector}")
                                break
                        except:
                            continue
                
                if not candidate_elements or len(candidate_elements) < 1:
                    logger.warning(f"⚠️  No candidate cards found on page {page_num}")
                    if page_num == 1:
                        # Save page source for debugging only on first page
                        logger.info("💾 Saving page source for debugging...")
                        with open("resdex_page_debug.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        logger.info("   Saved to: resdex_page_debug.html")
                    continue
            
                # Extract candidate information
                logger.info(f"📊 Extracting data from {len(candidate_elements)} candidates on page {page_num}...")
                
                # Find all candidate cards (the parent divs)
                candidate_cards = driver.find_elements(By.CSS_SELECTOR, "div.left-section")
            
                if not candidate_cards:
                    logger.warning("⚠️  Could not find candidate cards, trying alternative selector")
                    candidate_cards = driver.find_elements(By.CSS_SELECTOR, "div[class*='left-section'], div[class*='candidate']")
                
                logger.info(f"📋 Found {len(candidate_cards)} candidate cards on page {page_num}")
                
                page_candidates = []
                for i, card in enumerate(candidate_cards):
                    try:
                        # Extract name
                        name = "Candidate"
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, "a.candidate-name, [class*='candidate-name']")
                            name = name_elem.text.strip()
                        except:
                            pass
                        
                        # Extract current title and company
                        title = job_description.title
                        company = ""
                        try:
                            current_elem = card.find_element(By.CSS_SELECTOR, "#currentEmp, [id='currentEmp']")
                            current_text = current_elem.text.strip()
                            # Parse "Python Developer at Company Name"
                            if " at " in current_text:
                                parts = current_text.split(" at ")
                                title = parts[0].strip()
                                company = parts[1].strip() if len(parts) > 1 else ""
                            else:
                                title = current_text
                        except:
                            pass
                        
                        # Extract experience
                        experience = ""
                        try:
                            exp_elem = card.find_element(By.CSS_SELECTOR, "i.ico-work ~ span, [title*='Experience'] ~ span")
                            experience = exp_elem.text.strip()
                        except:
                            pass
                        
                        # Extract salary
                        salary = ""
                        try:
                            salary_elem = card.find_element(By.CSS_SELECTOR, "i.naukri-icon-account_balance_wallet ~ span")
                            salary = salary_elem.text.strip()
                        except:
                            pass
                        
                        # Extract location
                        location = job_description.location or ""
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, "span.location, i.ico-place ~ span")
                            location = location_elem.text.strip()
                        except:
                            pass
                        
                        # Extract education
                        education = []
                        try:
                            edu_elems = card.find_elements(By.CSS_SELECTOR, "#education .education")
                            for edu in edu_elems[:2]:
                                education.append(edu.text.strip())
                        except:
                            pass
                        
                        # Extract key skills
                        skills = []
                        try:
                            skill_elems = card.find_elements(By.CSS_SELECTOR, ".key-skills .cand-skill")
                            for skill_elem in skill_elems:
                                skill_text = skill_elem.text.strip().replace(" | ", "")
                                if skill_text:
                                    skills.append(skill_text)
                        except:
                            # Fallback to job description skills
                            skills = job_description.required_skills[:3]
                        
                        # Extract preferred locations
                        pref_locations = []
                        try:
                            pref_loc_elem = card.find_element(By.CSS_SELECTOR, "[title*='Hyderabad'], [title*='Bengaluru']")
                            pref_loc_text = pref_loc_elem.get_attribute("title")
                            if pref_loc_text:
                                pref_locations = [loc.strip() for loc in pref_loc_text.split(',')][:5]
                        except:
                            pass
                        
                        # Get profile URL
                        profile_url = search_url
                        try:
                            link_elem = card.find_element(By.CSS_SELECTOR, "a.candidate-name")
                            profile_url = link_elem.get_attribute("href")
                            if profile_url and not profile_url.startswith('http'):
                                profile_url = f"https://resdex.naukri.com{profile_url}"
                        except:
                            pass
                        
                        # Build summary
                        summary_parts = []
                        if company:
                            summary_parts.append(f"Current: {title} at {company}")
                        if experience:
                            summary_parts.append(f"Experience: {experience}")
                        if salary:
                            summary_parts.append(f"Salary: {salary}")
                        if education:
                            summary_parts.append(f"Education: {education[0]}")
                        
                        summary = " | ".join(summary_parts) if summary_parts else f"{title}"
                        
                        # Create candidate
                        candidate = Candidate(
                            id=hashlib.md5(f"naukri_resdex_{name}_{company}_{page_num}_{i}".encode()).hexdigest(),
                            name=name,
                            current_title=title,
                            skills=skills[:15],
                            location=location,
                            profile_url=profile_url,
                            source_portal="naukri_resdex",
                            summary=summary[:300]
                        )
                        page_candidates.append(candidate)
                        logger.info(f"  ✓ Page {page_num}.{i+1}. {name} - {title} ({len(skills)} skills)")
                        
                    except Exception as e:
                        logger.error(f"Error extracting candidate {i} on page {page_num}: {e}")
                        continue
                
                all_candidates.extend(page_candidates)
                logger.info(f"✅ Extracted {len(page_candidates)} candidates from page {page_num}")
                
                # Small delay between pages
                if page_num < max_pages:
                    await asyncio.sleep(2)
            
            candidates = all_candidates
            
        except Exception as e:
            logger.error(f"❌ Naukri Resdex scraping error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always close browser after scraping to prevent polling issues
            if driver:
                try:
                    logger.info("🔒 Closing Naukri browser...")
                    driver.quit()
                except:
                    pass
        
        logger.info(f"✅ Found {len(candidates)} candidates from Naukri Resdex")
        return candidates



class PortalScraperManager:
    """Manages multiple portal scrapers"""
    
    def __init__(self, config: dict):
        self.config = config
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> List[BasePortalScraper]:
        scrapers = []
        
        # Use LinkedIn Recruiter Lite for better results
        use_recruiter = self.config.get('linkedin', {}).get('use_recruiter', True)
        
        scraper_classes = {
            'linkedin': LinkedInScraper,  # ACTIVE
            # 'indeed': IndeedScraper,  # DISABLED - causing browser crashes
            'naukri': NaukriScraper,  # ACTIVE - Indian job portal
            'github_jobs': GitHubJobsScraper,  # ACTIVE
            'stackoverflow': StackOverflowScraper,  # ACTIVE
            # 'glassdoor': GlassdoorScraper,  # Disabled
            # 'coresignal': CoresignalScraper,  # Removed - not using API
        }
        
        for portal in self.config['job_portals']:
            if portal['enabled']:
                # Use LinkedIn Recruiter Lite if enabled
                if portal['name'] == 'linkedin' and use_recruiter:
                    from src.linkedin_recruiter_scraper import LinkedInRecruiterScraper
                    scrapers.append(LinkedInRecruiterScraper(self.config))
                    logger.info(f"✓ Initialized LinkedIn Recruiter Lite scraper")
                elif portal['name'] in scraper_classes:
                    scraper_class = scraper_classes[portal['name']]
                    scrapers.append(scraper_class(
                        portal['name'],
                        portal['base_url'],
                        self.config
                    ))
                    logger.info(f"Initialized scraper: {portal['name']}")
        
        return scrapers
    
    async def scrape_all_sequential(self, job_description: JobDescription) -> List[Candidate]:
        """Scrape all enabled portals sequentially (one at a time)"""
        logger.info(f"Starting sequential scraping from {len(self.scrapers)} portals")
        
        all_candidates = []
        seen_ids = set()
        
        for scraper in self.scrapers:
            try:
                logger.info(f"📍 Scraping {scraper.portal_name}...")
                candidates = await scraper.scrape(job_description)
                
                # Add unique candidates
                for candidate in candidates:
                    if candidate.id not in seen_ids:
                        all_candidates.append(candidate)
                        seen_ids.add(candidate.id)
                
                logger.info(f"✅ {scraper.portal_name}: {len(candidates)} candidates")
                
                # Save to vector DB after each scraper
                if candidates:
                    try:
                        from src.vector_db import CandidateVectorDB
                        vector_db = CandidateVectorDB()
                        vector_db.add_candidates(candidates)
                        logger.info(f"💾 Saved {len(candidates)} candidates to vector DB")
                    except Exception as e:
                        logger.warning(f"⚠️  Could not save to vector DB: {e}")
                
                # Delay between scrapers to ensure proper completion
                logger.info(f"⏸️  Waiting 5 seconds before next scraper...")
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {scraper.portal_name}: {e}")
                continue
        
        logger.info(f"✅ Total unique candidates: {len(all_candidates)}")
        return all_candidates
    
    async def scrape_all(self, job_description: JobDescription) -> List[Candidate]:
        """Scrape all enabled portals concurrently"""
        logger.info(f"Starting scraping from {len(self.scrapers)} portals")
        
        tasks = [scraper.scrape(job_description) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_candidates = []
        seen_ids = set()
        
        for result in results:
            if isinstance(result, list):
                for candidate in result:
                    if candidate.id not in seen_ids:
                        all_candidates.append(candidate)
                        seen_ids.add(candidate.id)
            else:
                logger.error(f"Scraping error: {result}")
        
        logger.info(f"Total unique candidates found: {len(all_candidates)}")
        return all_candidates
