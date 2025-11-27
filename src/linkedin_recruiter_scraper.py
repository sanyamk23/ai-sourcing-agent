"""
LinkedIn Recruiter Lite Scraper
Uses the advanced search with filters for better results
"""
import asyncio
import time
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from src.models import Candidate, JobDescription
import logging
import hashlib

logger = logging.getLogger(__name__)


class LinkedInRecruiterScraper:
    """Scraper for LinkedIn Recruiter Lite with advanced filters"""
    
    def __init__(self, config: dict):
        self.config = config
        self.driver = None
        self.is_logged_in = False
    
    def _get_driver(self, use_profile: bool = True):
        """Create Chrome driver with saved profile"""
        if use_profile:
            try:
                from src.browser_profile_manager import BrowserProfileManager
                driver = BrowserProfileManager.create_custom_profile_driver(
                    "./chrome_profile_linkedin",
                    headless=False
                )
                logger.info("Using Chrome profile with saved LinkedIn session")
                return driver
            except Exception as e:
                logger.warning(f"Could not load profile: {e}")
        
        # Fallback
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return uc.Chrome(options=options)
    
    async def scrape(self, job_description: JobDescription, max_candidates: int = 20) -> List[Candidate]:
        """Scrape using LinkedIn Recruiter Lite advanced search"""
        candidates = []
        
        try:
            self.driver = self._get_driver(use_profile=True)
            
            # Check if logged in
            logger.info("Checking LinkedIn login status...")
            self.driver.get("https://www.linkedin.com/talent/home")
            await asyncio.sleep(3)
            
            # If not on talent page, try to login or navigate
            if "talent" not in self.driver.current_url:
                logger.info("Not on Recruiter Lite, checking regular LinkedIn...")
                self.driver.get("https://www.linkedin.com/feed")
                await asyncio.sleep(2)
                
                if "feed" not in self.driver.current_url:
                    logger.error("Not logged in to LinkedIn. Please run: python setup_linkedin_cookies.py")
                    return candidates
                
                # Navigate to Recruiter Lite
                logger.info("Navigating to Recruiter Lite...")
                self.driver.get("https://www.linkedin.com/talent/home")
                await asyncio.sleep(3)
            
            logger.info("✅ On LinkedIn Recruiter Lite")
            
            # Click on "Start new Recruiter search" or use advanced search
            logger.info("Starting advanced search...")
            
            # Navigate directly to advanced search
            self.driver.get("https://www.linkedin.com/talent/search?start=0&uiOrigin=GLOBAL_SEARCH_HEADER")
            await asyncio.sleep(3)
            
            logger.info("✅ On advanced search page")
            
            # Try to use the main search box first (simpler approach)
            try:
                logger.info("Trying main search box...")
                search_box = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='search']")
                search_query = f"{job_description.title} {' '.join(job_description.required_skills[:3])}"
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
                await asyncio.sleep(5)
                logger.info("✓ Search via main search box")
            except:
                logger.info("Main search box not found, using filters...")
            
            # Add filters one by one
            logger.info("Adding search filters...")
            
            # Add Job Title filter
            await self._add_job_title_filter(job_description.title)
            await asyncio.sleep(2)
            
            # Add Skills filter
            if job_description.required_skills:
                await self._add_skills_filter(job_description.required_skills)
                await asyncio.sleep(2)
            
            # Add Location filter
            if job_description.location:
                await self._add_location_filter(job_description.location)
                await asyncio.sleep(2)
            
            # Add Experience filter
            if job_description.experience_years:
                await self._add_experience_filter(job_description.experience_years)
                await asyncio.sleep(2)
            
            logger.info("✅ All filters added")
            
            # Click Search button (or wait for auto-search)
            await self._click_search()
            
            # Wait for results to load
            logger.info("Waiting for search results...")
            await asyncio.sleep(8)
            
            # Extract candidates from results
            candidates = await self._extract_candidates(max_candidates)
            
            logger.info(f"✅ Scraped {len(candidates)} candidates from LinkedIn Recruiter")
            
        except Exception as e:
            logger.error(f"Error in LinkedIn Recruiter scraping: {e}", exc_info=True)
        finally:
            if self.driver:
                self.driver.quit()
        
        return candidates
    
    async def _add_job_title_filter(self, title: str):
        """Add job title filter"""
        try:
            logger.info(f"Adding job title filter: {title}")
            
            # Click on "Job titles" button
            job_title_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Job titles')]")
            job_title_button.click()
            await asyncio.sleep(1)
            
            # Find input field and enter title
            input_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='job title']")
            input_field.send_keys(title)
            await asyncio.sleep(1)
            input_field.send_keys(Keys.RETURN)
            await asyncio.sleep(1)
            
            logger.info("✓ Job title filter added")
        except Exception as e:
            logger.warning(f"Could not add job title filter: {e}")
    
    async def _add_skills_filter(self, skills: List[str]):
        """Add skills filter"""
        try:
            logger.info(f"Adding skills filter: {skills}")
            
            # Click on "Skills and Assessments" or "Skill keywords"
            skills_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Skill keywords')]")
            skills_button.click()
            await asyncio.sleep(1)
            
            # Add each skill
            for skill in skills[:5]:  # Limit to 5 skills
                try:
                    input_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='skill']")
                    input_field.send_keys(skill)
                    await asyncio.sleep(0.5)
                    input_field.send_keys(Keys.RETURN)
                    await asyncio.sleep(0.5)
                except:
                    continue
            
            logger.info("✓ Skills filter added")
        except Exception as e:
            logger.warning(f"Could not add skills filter: {e}")
    
    async def _add_location_filter(self, location: str):
        """Add location filter"""
        try:
            logger.info(f"Adding location filter: {location}")
            
            # Click on "Locations" button
            location_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Locations')]")
            location_button.click()
            await asyncio.sleep(1)
            
            # Find input and enter location
            input_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='location']")
            input_field.send_keys(location)
            await asyncio.sleep(1)
            input_field.send_keys(Keys.RETURN)
            await asyncio.sleep(1)
            
            logger.info("✓ Location filter added")
        except Exception as e:
            logger.warning(f"Could not add location filter: {e}")
    
    async def _add_experience_filter(self, years: int):
        """Add years of experience filter"""
        try:
            logger.info(f"Adding experience filter: {years}+ years")
            
            # Click on "Years of experience"
            exp_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Years of experience')]")
            exp_button.click()
            await asyncio.sleep(1)
            
            # Select appropriate range based on years
            if years >= 10:
                checkbox = self.driver.find_element(By.XPATH, "//label[contains(text(), '10+')]")
            elif years >= 5:
                checkbox = self.driver.find_element(By.XPATH, "//label[contains(text(), '5-10')]")
            elif years >= 2:
                checkbox = self.driver.find_element(By.XPATH, "//label[contains(text(), '2-5')]")
            else:
                checkbox = self.driver.find_element(By.XPATH, "//label[contains(text(), '0-2')]")
            
            checkbox.click()
            await asyncio.sleep(1)
            
            logger.info("✓ Experience filter added")
        except Exception as e:
            logger.warning(f"Could not add experience filter: {e}")
    
    async def _click_search(self):
        """Click the Search button or wait for auto-search"""
        try:
            logger.info("Looking for Search button...")
            
            # Try multiple selectors for Search button
            search_selectors = [
                "//button[contains(text(), 'Search')]",
                "//button[@data-test-search-button]",
                "//button[contains(@class, 'search-button')]",
                "button[type='submit']"
            ]
            
            search_clicked = False
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        search_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    search_button.click()
                    logger.info("✓ Search button clicked")
                    search_clicked = True
                    break
                except:
                    continue
            
            if not search_clicked:
                logger.info("ℹ️  No search button found - LinkedIn Recruiter may auto-search")
                logger.info("Waiting for results to load...")
            
        except Exception as e:
            logger.info(f"Search button not needed or auto-search enabled: {e}")
    
    async def _extract_candidates(self, max_candidates: int) -> List[Candidate]:
        """Extract candidate data from search results"""
        candidates = []
        
        try:
            logger.info("Extracting candidates from results...")
            
            # Scroll to load more results
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Find all candidate cards
            candidate_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-search-result]")
            
            if not candidate_cards:
                # Try alternative selector
                candidate_cards = self.driver.find_elements(By.CSS_SELECTOR, ".search-results__result-item")
            
            logger.info(f"Found {len(candidate_cards)} candidate cards")
            
            for i, card in enumerate(candidate_cards[:max_candidates]):
                try:
                    # Extract name
                    name = "LinkedIn User"
                    try:
                        name_elem = card.find_element(By.CSS_SELECTOR, "[data-test-search-result-person-name]")
                        name = name_elem.text.strip()
                    except:
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, "a[data-control-name='view_profile']")
                            name = name_elem.text.strip()
                        except:
                            pass
                    
                    # Extract title
                    title = ""
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "[data-test-search-result-person-headline]")
                        title = title_elem.text.strip()
                    except:
                        pass
                    
                    # Extract location
                    location = ""
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, "[data-test-search-result-person-location]")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    # Extract profile URL
                    profile_url = ""
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, "a[href*='/talent/profile/']")
                        profile_url = link_elem.get_attribute("href")
                    except:
                        pass
                    
                    # Create candidate
                    if name and name != "LinkedIn User":
                        candidate_id = hashlib.md5(f"{name}{title}".encode()).hexdigest()
                        
                        candidate = Candidate(
                            id=candidate_id,
                            name=name,
                            current_title=title,
                            location=location,
                            profile_url=profile_url,
                            source_portal="LinkedIn Recruiter",
                            skills=[],  # Will be enriched later
                            experience_years=0  # Will be enriched later
                        )
                        
                        candidates.append(candidate)
                        logger.info(f"✓ Extracted: {name} - {title}")
                
                except Exception as e:
                    logger.warning(f"Error extracting candidate {i}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in candidate extraction: {e}")
        
        return candidates
