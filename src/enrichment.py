import aiohttp
import os
from typing import Optional
from src.models import Candidate
import logging

logger = logging.getLogger(__name__)

class CandidateEnricher:
    """Enrich candidate data with additional information"""
    
    def __init__(self):
        self.clearbit_key = os.getenv('CLEARBIT_API_KEY')
        self.hunter_key = os.getenv('HUNTER_API_KEY')
    
    async def enrich_candidate(self, candidate: Candidate) -> Candidate:
        """Enrich candidate with email, phone, and additional data"""
        
        # Try to find email if missing
        if not candidate.email and candidate.name:
            candidate.email = await self._find_email(candidate)
        
        # Enrich with Clearbit if available
        if self.clearbit_key and candidate.email:
            enriched_data = await self._enrich_with_clearbit(candidate.email)
            if enriched_data:
                candidate = self._merge_enriched_data(candidate, enriched_data)
        
        return candidate
    
    async def _find_email(self, candidate: Candidate) -> Optional[str]:
        """Find email using Hunter.io"""
        if not self.hunter_key:
            return None
        
        try:
            # Extract company domain from profile URL or current title
            domain = self._extract_domain(candidate.profile_url)
            if not domain:
                return None
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.hunter.io/v2/email-finder"
                params = {
                    'domain': domain,
                    'first_name': candidate.name.split()[0] if candidate.name else '',
                    'last_name': candidate.name.split()[-1] if candidate.name and len(candidate.name.split()) > 1 else '',
                    'api_key': self.hunter_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get('email')
        
        except Exception as e:
            logger.error(f"Email finder error: {e}")
        
        return None
    
    async def _enrich_with_clearbit(self, email: str) -> Optional[dict]:
        """Enrich with Clearbit Person API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://person.clearbit.com/v2/people/find?email={email}"
                headers = {'Authorization': f'Bearer {self.clearbit_key}'}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
        
        except Exception as e:
            logger.error(f"Clearbit enrichment error: {e}")
        
        return None
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return None
    
    def _merge_enriched_data(self, candidate: Candidate, enriched: dict) -> Candidate:
        """Merge enriched data into candidate"""
        if not enriched:
            return candidate
        
        # Update fields if not already set
        if not candidate.location and enriched.get('location'):
            candidate.location = enriched['location']
        
        if not candidate.current_title and enriched.get('employment', {}).get('title'):
            candidate.current_title = enriched['employment']['title']
        
        # Add social profiles to summary
        if enriched.get('twitter', {}).get('handle'):
            twitter = enriched['twitter']['handle']
            candidate.summary = f"{candidate.summary or ''} | Twitter: @{twitter}"
        
        return candidate
