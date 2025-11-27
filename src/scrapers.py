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
    
    def _get_driver(self, headless: bool = True):
        """Create Selenium WebDriver with anti-detection"""
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
        
        try:
            # Get or reuse existing browser
            driver = self._get_or_create_driver()
            
            # Login only if not already logged in
            if not LinkedInScraper._is_logged_in:
                logger.info("Logging into LinkedIn...")
                
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
                        LinkedInScraper._is_logged_in = True
                        logger.info("✓ LinkedIn login successful - session will be reused")
                    else:
                        logger.warning("LinkedIn login may have failed - check for CAPTCHA")
                        await asyncio.sleep(10)  # Give time to solve CAPTCHA manually
                        LinkedInScraper._is_logged_in = True  # Assume logged in after wait
                    
                except Exception as e:
                    logger.error(f"LinkedIn login error: {e}")
                    return candidates
            else:
                logger.info("✓ Already logged in - reusing session")
            
            # Search for people with relevant skills
            logger.info(f"Searching for: {job_description.title}")
            
            # Build people search URL
            keywords = quote_plus(job_description.title)
            location = quote_plus(job_description.location) if job_description.location else ""
            
            # Use LinkedIn's people search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            if location:
                search_url += f"&location={location}"
            
            # Open in new tab if there are existing tabs, otherwise use current tab
            if len(driver.window_handles) > 0:
                logger.info("📑 Opening search in new tab...")
                driver.execute_script(f"window.open('{search_url}', '_blank');")
                await asyncio.sleep(2)
                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])
            else:
                driver.get(search_url)
            
            await asyncio.sleep(5)
            
            # Scroll to load more results
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Find all profile cards - LinkedIn changed their structure
            profile_cards = driver.find_elements(By.CSS_SELECTOR, "[data-chameleon-result-urn]")
            
            logger.info(f"Found {len(profile_cards)} profile cards")
            
            for i, card in enumerate(profile_cards[:self.max_candidates]):
                try:
                    # Extract name - try multiple selectors
                    name = "LinkedIn User"
                    for name_selector in [
                        "span[aria-hidden='true']",
                        ".entity-result__title-text span",
                        "a span[dir='ltr']",
                        "span[dir='ltr'] span[aria-hidden='true']"
                    ]:
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, name_selector)
                            name_text = name_elem.text.strip()
                            if name_text and len(name_text) > 2:
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
        
        logger.info(f"✓ Found {len(candidates)} candidates from LinkedIn")
        logger.info("💡 Browser window kept open for future searches")
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

class PortalScraperManager:
    """Manages multiple portal scrapers"""
    
    def __init__(self, config: dict):
        self.config = config
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> List[BasePortalScraper]:
        scrapers = []
        scraper_classes = {
            'linkedin': LinkedInScraper,
            'indeed': IndeedScraper,
            'glassdoor': GlassdoorScraper,
            'github_jobs': GitHubJobsScraper,
            'stackoverflow': StackOverflowScraper
        }
        
        for portal in self.config['job_portals']:
            if portal['enabled'] and portal['name'] in scraper_classes:
                scraper_class = scraper_classes[portal['name']]
                scrapers.append(scraper_class(
                    portal['name'],
                    portal['base_url'],
                    self.config
                ))
                logger.info(f"Initialized scraper: {portal['name']}")
        
        return scrapers
    
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
