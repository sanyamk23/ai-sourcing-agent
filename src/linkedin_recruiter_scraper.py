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
            
            # Click the facet edit button for job titles
            button_texts = [
                "Job titles or boolean",
                "Add a Job title",
                "Job titles"
            ]
            
            for text in button_texts:
                try:
                    add_button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(@class, 'facet-edit-button')]//span[contains(text(), '{text}')]/.."
                    )
                    add_button.click()
                    await asyncio.sleep(1)
                    break
                except:
                    continue
            
            # Find input field - try multiple selectors
            input_selectors = [
                "//input[@placeholder='Job titles or boolean']",
                "//input[contains(@placeholder, 'job title')]",
                "//input[contains(@placeholder, 'Job title')]"
            ]
            
            for selector in input_selectors:
                try:
                    input_field = self.driver.find_element(By.XPATH, selector)
                    input_field.clear()
                    input_field.send_keys(title)
                    await asyncio.sleep(1)
                    input_field.send_keys(Keys.RETURN)
                    await asyncio.sleep(1)
                    logger.info("✓ Job title filter added")
                    return
                except:
                    continue
            
            logger.warning("Could not find job title input field")
            
        except Exception as e:
            logger.warning(f"Could not add job title filter: {e}")
    
    async def _add_skills_filter(self, skills: List[str]):
        """Add skills filter"""
        try:
            logger.info(f"Adding skills filter: {skills}")
            
            # Click the facet edit button for skills
            button_texts = [
                "Skill keywords anywhere on profile",
                "Add a Skill keyword",
                "Skills",
                "Skill keywords"
            ]
            
            for text in button_texts:
                try:
                    add_button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(@class, 'facet-edit-button')]//span[contains(text(), '{text}')]/.."
                    )
                    add_button.click()
                    await asyncio.sleep(1)
                    break
                except:
                    continue
            
            # Find input field
            input_selectors = [
                "//input[@placeholder='Skill keywords anywhere on profile']",
                "//input[contains(@placeholder, 'Skill keyword')]",
                "//input[contains(@placeholder, 'skill')]"
            ]
            
            for selector in input_selectors:
                try:
                    input_field = self.driver.find_element(By.XPATH, selector)
                    
                    # Add each skill
                    for skill in skills[:5]:  # Limit to 5 skills
                        try:
                            input_field.clear()
                            input_field.send_keys(skill)
                            await asyncio.sleep(0.5)
                            input_field.send_keys(Keys.RETURN)
                            await asyncio.sleep(0.5)
                        except:
                            continue
                    
                    logger.info("✓ Skills filter added")
                    return
                except:
                    continue
            
            logger.warning("Could not find skills input field")
            
        except Exception as e:
            logger.warning(f"Could not add skills filter: {e}")
    
    async def _add_location_filter(self, location: str):
        """Add location filter"""
        try:
            logger.info(f"Adding location filter: {location}")
            
            # Click the facet edit button for locations
            button_texts = [
                "Candidate geographic locations",
                "Add a Candidate geographic location",
                "Locations"
            ]
            
            for text in button_texts:
                try:
                    add_button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(@class, 'facet-edit-button')]//span[contains(text(), '{text}')]/.."
                    )
                    add_button.click()
                    await asyncio.sleep(1)
                    break
                except:
                    continue
            
            # Find input field
            input_selectors = [
                "//input[@placeholder='Candidate geographic locations']",
                "//input[contains(@placeholder, 'geographic location')]",
                "//input[contains(@placeholder, 'location')]"
            ]
            
            for selector in input_selectors:
                try:
                    input_field = self.driver.find_element(By.XPATH, selector)
                    input_field.clear()
                    input_field.send_keys(location)
                    await asyncio.sleep(2)  # Wait for dropdown
                    input_field.send_keys(Keys.ARROW_DOWN)
                    await asyncio.sleep(0.5)
                    input_field.send_keys(Keys.RETURN)
                    await asyncio.sleep(1)
                    logger.info("✓ Location filter added")
                    return
                except:
                    continue
            
            logger.warning("Could not find location input field")
            
        except Exception as e:
            logger.warning(f"Could not add location filter: {e}")
    
    async def _add_experience_filter(self, years: int):
        """Add years of experience filter"""
        try:
            logger.info(f"Adding experience filter: {years}+ years")
            
            # Click the facet edit button for experience
            button_texts = [
                "Years of experience",
                "Add Years of experience",
                "Experience"
            ]
            
            clicked = False
            for text in button_texts:
                try:
                    add_button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(@class, 'facet-edit-button')]//span[contains(text(), '{text}')]/.."
                    )
                    add_button.click()
                    await asyncio.sleep(1)
                    clicked = True
                    break
                except:
                    continue
            
            if not clicked:
                logger.warning("Could not find experience button")
                return
            
            # Select appropriate range based on years
            checkbox_texts = []
            if years >= 10:
                checkbox_texts = ["10+", "10 or more", "10+ years"]
            elif years >= 5:
                checkbox_texts = ["5-10", "5 to 10", "5-10 years"]
            elif years >= 2:
                checkbox_texts = ["2-5", "2 to 5", "2-5 years"]
            else:
                checkbox_texts = ["0-2", "0 to 2", "0-2 years", "1-2"]
            
            for text in checkbox_texts:
                try:
                    checkbox = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{text}')]")
                    checkbox.click()
                    await asyncio.sleep(1)
                    logger.info("✓ Experience filter added")
                    return
                except:
                    continue
            
            logger.warning("Could not find experience checkbox")
            
        except Exception as e:
            logger.warning(f"Could not add experience filter: {e}")
    
    def _calculate_total_experience(self, experience_items) -> int:
        """Calculate total years of experience from experience items"""
        import re
        from datetime import datetime
        
        total_years = 0
        current_year = datetime.now().year
        
        for item in experience_items:
            try:
                text = item.text
                
                # Look for date patterns like "2024 – Present", "2023 – 2024", etc.
                # Pattern: YYYY – YYYY or YYYY – Present
                date_pattern = r'(\d{4})\s*[–-]\s*(Present|\d{4})'
                matches = re.findall(date_pattern, text)
                
                for match in matches:
                    start_year = int(match[0])
                    end_year = current_year if match[1] == "Present" else int(match[1])
                    
                    years = end_year - start_year
                    if years < 0:
                        years = 0
                    
                    total_years += years
                    
            except Exception as e:
                logger.debug(f"Error parsing experience date: {e}")
                continue
        
        return total_years
    
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
            
            # Wait for results to load
            await asyncio.sleep(3)
            
            # Scroll to load more results
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                logger.info(f"Scrolled {i+1}/3")
            
            # Try multiple selectors for candidate cards
            candidate_cards = []
            selectors = [
                "article.profile-list-item",  # LinkedIn Recruiter Lite profile cards
                "li.artdeco-list__item",
                "[data-test-search-result]",
                ".search-results__result-item",
                "div.entity-result",
                "li[class*='search-result']"
            ]
            
            for selector in selectors:
                candidate_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if candidate_cards:
                    logger.info(f"✓ Found {len(candidate_cards)} candidate cards using: {selector}")
                    break
                else:
                    logger.warning(f"No cards with selector: {selector}")
            
            if not candidate_cards:
                logger.error("❌ Could not find any candidate cards!")
                logger.info("Page source preview:")
                logger.info(self.driver.page_source[:1000])
                return candidates
            
            logger.info(f"Processing {min(len(candidate_cards), max_candidates)} candidates...")
            
            for i, card in enumerate(candidate_cards[:max_candidates]):
                try:
                    # Extract name - try multiple approaches
                    name = "LinkedIn User"
                    name_selectors = [
                        "div.artdeco-entity-lockup__title a",  # Main name link
                        "span[data-test-row-lockup-full-name] a",
                        "a[data-test-link-to-profile-link]",
                        "span.artdeco-entity-lockup__title",
                        "a.app-aware-link span[aria-hidden='true']",
                        "[data-test-search-result-person-name]",
                        "a[data-control-name='view_profile']"
                    ]
                    
                    for selector in name_selectors:
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, selector)
                            name_text = name_elem.text.strip()
                            if name_text and len(name_text) > 2:
                                name = name_text
                                break
                        except:
                            continue
                    
                    # Extract title/headline
                    title = ""
                    title_selectors = [
                        "span[data-test-row-lockup-headline]",  # Main headline
                        "div.artdeco-entity-lockup__subtitle span",
                        "span.artdeco-entity-lockup__subtitle",
                        "div.artdeco-entity-lockup__subtitle",
                        "[data-test-search-result-person-headline]"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, selector)
                            title = title_elem.text.strip()
                            if title:
                                break
                        except:
                            continue
                    
                    # Extract location
                    location = ""
                    location_selectors = [
                        "div[data-test-row-lockup-location]",  # Main location
                        "div.artdeco-entity-lockup__metadata div",
                        "span.artdeco-entity-lockup__caption",
                        "div.artdeco-entity-lockup__caption",
                        "[data-test-search-result-person-location]"
                    ]
                    
                    for selector in location_selectors:
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, selector)
                            location = location_elem.text.strip()
                            if location and "·" not in location:  # Skip if it contains separator
                                break
                        except:
                            continue
                    
                    # Extract profile URL
                    profile_url = ""
                    url_selectors = [
                        "a[href*='/talent/profile/']",  # Recruiter profile URL
                        "div.artdeco-entity-lockup__title a",
                        "a[data-test-link-to-profile-link]",
                        "a[href*='/in/']",
                        "a.app-aware-link"
                    ]
                    
                    for selector in url_selectors:
                        try:
                            link_elem = card.find_element(By.CSS_SELECTOR, selector)
                            profile_url = link_elem.get_attribute("href")
                            if profile_url and ("/talent/profile/" in profile_url or "/in/" in profile_url):
                                break
                        except:
                            continue
                    
                    # Extract experience years
                    experience_years = 0
                    experience_text = ""
                    try:
                        # Look for the experience section in the history
                        experience_section = card.find_element(By.CSS_SELECTOR, "div[data-test-history]")
                        
                        # Get all experience entries
                        experience_items = experience_section.find_elements(
                            By.CSS_SELECTOR, 
                            "li[data-test-description-description]"
                        )
                        
                        # Calculate total years from all experience entries
                        experience_years = self._calculate_total_experience(experience_items)
                        
                        # Store experience text for reference
                        if experience_items:
                            experience_text = " | ".join([item.text.strip() for item in experience_items[:3]])
                        
                        logger.info(f"  → Experience: {experience_years} years")
                    except Exception as e:
                        logger.debug(f"Could not extract experience for {name}: {e}")
                    
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
                            experience_years=experience_years,
                            experience=experience_text if experience_text else None
                        )
                        
                        candidates.append(candidate)
                        logger.info(f"✓ Extracted: {name} - {title} ({experience_years} yrs exp)")
                
                except Exception as e:
                    logger.warning(f"Error extracting candidate {i}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in candidate extraction: {e}")
        
        return candidates
