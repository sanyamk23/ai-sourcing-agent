"""
MCP (Model Context Protocol) Tools for Scraping
Exposes scrapers as tools that LLM can orchestrate
"""

import asyncio
import json
from typing import List, Dict, Any
from src.models import JobDescription, Candidate
from src.scrapers import (
    NaukriScraper,
    IndeedScraper,
    GlassdoorScraper,
    GitHubJobsScraper,
    StackOverflowScraper
)
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class ScraperMCPTools:
    """MCP Tools for candidate scraping - allows LLM to orchestrate scraping"""
    
    def __init__(self, config: dict):
        self.config = config
        self._init_scrapers()
    
    def _init_scrapers(self):
        """Initialize all available scrapers"""
        from src.scrapers import LinkedInScraper
        
        self.scrapers = {
            'linkedin': LinkedInScraper('linkedin', 'https://www.linkedin.com', self.config),
            'naukri': NaukriScraper('naukri', 'https://www.naukri.com', self.config),
            'indeed': IndeedScraper('indeed', 'https://www.indeed.com', self.config),
            'github': GitHubJobsScraper('github_jobs', 'https://github.com', self.config),
            'stackoverflow': StackOverflowScraper('stackoverflow', 'https://stackoverflow.com', self.config),
            'glassdoor': GlassdoorScraper('glassdoor', 'https://www.glassdoor.com', self.config),
        }
        logger.info(f"Initialized {len(self.scrapers)} scraper tools")
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Return MCP tools schema for LLM"""
        return [
            {
                "name": "scrape_linkedin",
                "description": "Search for candidates on LinkedIn. Best for: professional profiles, detailed experience, connections. Requires LinkedIn credentials.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Job title to search for"},
                        "location": {"type": "string", "description": "Location (e.g., 'Jaipur', 'India')"},
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Required skills"},
                        "experience_years": {"type": "integer", "description": "Minimum years of experience"}
                    },
                    "required": ["job_title"]
                }
            },
            {
                "name": "scrape_naukri",
                "description": "Search for candidates on Naukri.com (India's largest job portal). Best for: Indian candidates, active job seekers, recent postings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Job title to search for"},
                        "location": {"type": "string", "description": "Location in India"},
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Required skills"},
                        "experience_years": {"type": "integer", "description": "Minimum years of experience"}
                    },
                    "required": ["job_title"]
                }
            },
            {
                "name": "scrape_indeed",
                "description": "Search for candidates on Indeed.com (global job portal). Best for: diverse locations, various industries, job postings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Job title to search for"},
                        "location": {"type": "string", "description": "Location"},
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Required skills"}
                    },
                    "required": ["job_title"]
                }
            },
            {
                "name": "scrape_github",
                "description": "Search for developers on GitHub. Best for: open-source contributors, developers with public repos, technical profiles.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Programming languages/skills to search for"}
                    },
                    "required": ["skills"]
                }
                },
            {
                "name": "scrape_all_parallel",
                "description": "Run multiple scrapers in parallel for maximum coverage. Recommended for comprehensive candidate search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Job title to search for"},
                        "location": {"type": "string", "description": "Location"},
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Required skills"},
                        "experience_years": {"type": "integer", "description": "Minimum years of experience"},
                        "scrapers": {"type": "array", "items": {"type": "string"}, "description": "List of scrapers to use (e.g., ['coresignal', 'naukri'])"}
                    },
                    "required": ["job_title", "scrapers"]
                }
            }
        ]
    
    async def scrape_linkedin(self, job_title: str, location: str = None, 
                             skills: List[str] = None, experience_years: int = None) -> Dict[str, Any]:
        """Scrape LinkedIn"""
        logger.info(f"🔧 MCP Tool: scrape_linkedin({job_title}, {location})")
        
        job_desc = JobDescription(
            title=job_title,
            description=f"Looking for {job_title}",
            required_skills=skills or [],
            experience_years=experience_years,
            location=location
        )
        
        candidates = await self.scrapers['linkedin'].scrape(job_desc)
        
        return {
            "source": "linkedin",
            "count": len(candidates),
            "candidates": [c.dict() for c in candidates]
        }
    
    async def scrape_naukri(self, job_title: str, location: str = None,
                           skills: List[str] = None, experience_years: int = None) -> Dict[str, Any]:
        """Scrape Naukri.com"""
        logger.info(f"🔧 MCP Tool: scrape_naukri({job_title}, {location})")
        
        job_desc = JobDescription(
            title=job_title,
            description=f"Looking for {job_title}",
            required_skills=skills or [],
            experience_years=experience_years,
            location=location or "India"
        )
        
        candidates = await self.scrapers['naukri'].scrape(job_desc)
        
        return {
            "source": "naukri",
            "count": len(candidates),
            "candidates": [c.dict() for c in candidates]
        }
    
    async def scrape_indeed(self, job_title: str, location: str = None,
                           skills: List[str] = None) -> Dict[str, Any]:
        """Scrape Indeed.com"""
        logger.info(f"🔧 MCP Tool: scrape_indeed({job_title}, {location})")
        
        job_desc = JobDescription(
            title=job_title,
            description=f"Looking for {job_title}",
            required_skills=skills or [],
            location=location
        )
        
        candidates = await self.scrapers['indeed'].scrape(job_desc)
        
        return {
            "source": "indeed",
            "count": len(candidates),
            "candidates": [c.dict() for c in candidates]
        }
    
    async def scrape_github(self, skills: List[str]) -> Dict[str, Any]:
        """Scrape GitHub"""
        logger.info(f"🔧 MCP Tool: scrape_github({skills})")
        
        job_desc = JobDescription(
            title="Developer",
            description="Looking for developers",
            required_skills=skills
        )
        
        candidates = await self.scrapers['github'].scrape(job_desc)
        
        return {
            "source": "github",
            "count": len(candidates),
            "candidates": [c.dict() for c in candidates]
        }
    
    async def scrape_all_parallel(self, job_title: str, scrapers: List[str],
                                  location: str = None, skills: List[str] = None,
                                  experience_years: int = None) -> Dict[str, Any]:
        """Run multiple scrapers in parallel"""
        logger.info(f"🔧 MCP Tool: scrape_all_parallel with {len(scrapers)} scrapers")
        
        job_desc = JobDescription(
            title=job_title,
            description=f"Looking for {job_title}",
            required_skills=skills or [],
            experience_years=experience_years,
            location=location
        )
        
        # Create tasks for parallel execution
        tasks = []
        for scraper_name in scrapers:
            if scraper_name in self.scrapers:
                tasks.append(self.scrapers[scraper_name].scrape(job_desc))
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_candidates = []
        seen_ids = set()
        sources_used = []
        
        for idx, result in enumerate(results):
            scraper_name = scrapers[idx]
            if isinstance(result, list):
                sources_used.append(scraper_name)
                for candidate in result:
                    if candidate.id not in seen_ids:
                        all_candidates.append(candidate)
                        seen_ids.add(candidate.id)
            else:
                logger.error(f"Error from {scraper_name}: {result}")
        
        return {
            "sources": sources_used,
            "total_count": len(all_candidates),
            "candidates": [c.dict() for c in all_candidates],
            "by_source": {
                scraper_name: len([c for c in all_candidates if c.source_portal == scraper_name])
                for scraper_name in sources_used
            }
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool_map = {
            "scrape_linkedin": self.scrape_linkedin,
            "scrape_naukri": self.scrape_naukri,
            "scrape_indeed": self.scrape_indeed,
            "scrape_github": self.scrape_github,
            "scrape_all_parallel": self.scrape_all_parallel
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return await tool_map[tool_name](**parameters)
