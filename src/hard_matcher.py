"""
Hard Matcher - Strict skill and experience matching
"""
from typing import List, Dict, Set
from src.models import Candidate, JobDescription
import logging

logger = logging.getLogger(__name__)

class HardMatcher:
    """Hard matching based on exact skills and experience requirements"""
    
    def __init__(self):
        pass
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        return skill.lower().strip().replace('-', '').replace('_', '').replace('.', '')
    
    def _get_matched_skills(self, job_skills: List[str], candidate_skills: List[str]) -> Set[str]:
        """Get skills that match between job and candidate"""
        # Normalize all skills
        job_skills_norm = {self._normalize_skill(s): s for s in job_skills}
        candidate_skills_norm = {self._normalize_skill(s): s for s in candidate_skills}
        
        # Find matches
        matched_normalized = set(job_skills_norm.keys()) & set(candidate_skills_norm.keys())
        
        # Return original skill names from job description
        matched_skills = {job_skills_norm[norm] for norm in matched_normalized}
        
        return matched_skills
    
    def _extract_skills_from_text(self, text: str, job_skills: List[str]) -> List[str]:
        """Extract skills from text (title, summary) by matching against job skills"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in job_skills:
            skill_norm = self._normalize_skill(skill)
            if skill_norm in self._normalize_skill(text):
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_skill_match_score(self, job_skills: List[str], candidate_skills: List[str]) -> float:
        """Calculate skill match percentage"""
        if not job_skills:
            return 1.0
        
        matched = self._get_matched_skills(job_skills, candidate_skills)
        return len(matched) / len(job_skills)
    
    def _calculate_experience_match_score(self, required_years: int, candidate_years: int) -> float:
        """Calculate experience match score"""
        if required_years == 0:
            return 1.0
        
        if candidate_years >= required_years:
            # Perfect match or overqualified
            return 1.0
        elif candidate_years >= required_years * 0.7:
            # Close enough (70% of required)
            return 0.8
        elif candidate_years >= required_years * 0.5:
            # Somewhat close (50% of required)
            return 0.5
        else:
            # Too junior
            return 0.2
    
    def match_candidates(
        self, 
        job: JobDescription, 
        candidates: List[Candidate],
        min_skill_match: float = 0.3,  # At least 30% skills must match
        min_experience_match: float = 0.5  # At least 50% experience requirement
    ) -> List[Dict]:
        """
        Hard match candidates based on skills and experience
        
        Returns list of dicts with candidate and match details
        """
        logger.info(f"🎯 Hard matching {len(candidates)} candidates")
        logger.info(f"   Required skills: {job.required_skills}")
        logger.info(f"   Required experience: {job.experience_years or 0} years")
        logger.info(f"   Min skill match: {min_skill_match * 100}%")
        logger.info(f"   Min experience match: {min_experience_match * 100}%")
        
        matched = []
        
        for candidate in candidates:
            # If candidate has no skills, try to extract from title/summary
            candidate_skills = candidate.skills if candidate.skills else []
            if not candidate_skills:
                # Extract skills from title and summary
                title_skills = self._extract_skills_from_text(candidate.current_title or '', job.required_skills)
                summary_skills = self._extract_skills_from_text(candidate.summary or '', job.required_skills)
                candidate_skills = list(set(title_skills + summary_skills))
            
            # Calculate skill match
            matched_skills = self._get_matched_skills(job.required_skills, candidate_skills)
            skill_score = self._calculate_skill_match_score(job.required_skills, candidate_skills)
            
            # Calculate experience match
            candidate_exp = candidate.experience_years or 0
            required_exp = job.experience_years or 0
            exp_score = self._calculate_experience_match_score(required_exp, candidate_exp)
            
            # Combined score (60% skills, 40% experience)
            combined_score = (0.6 * skill_score) + (0.4 * exp_score)
            
            # Check if meets minimum requirements
            if skill_score >= min_skill_match and exp_score >= min_experience_match:
                matched.append({
                    'candidate': candidate,
                    'skill_score': skill_score,
                    'experience_score': exp_score,
                    'combined_score': combined_score,
                    'matched_skills': list(matched_skills),
                    'missing_skills': list(set(job.required_skills) - matched_skills),
                    'experience_gap': max(0, required_exp - candidate_exp)
                })
        
        # Sort by combined score
        matched.sort(key=lambda x: x['combined_score'], reverse=True)
        
        logger.info(f"✅ {len(matched)} candidates passed hard matching")
        if matched:
            top_scores = [f"{m['candidate'].name}: {m['combined_score']:.2f}" for m in matched[:3]]
            logger.info(f"   Top 3 scores: {top_scores}")
        
        return matched
    
    def balance_by_source(
        self, 
        matched_candidates: List[Dict], 
        max_results: int = 10,
        sources: List[str] = ['naukri', 'linkedin', 'stackoverflow', 'github']
    ) -> List[Dict]:
        """
        Balance results to get equal representation from each source
        
        Args:
            matched_candidates: List of matched candidate dicts
            max_results: Maximum number of results to return
            sources: List of source portals to balance
        """
        logger.info(f"⚖️  Balancing {len(matched_candidates)} candidates across sources")
        
        # Group by source
        by_source = {source: [] for source in sources}
        for match in matched_candidates:
            source = match['candidate'].source_portal.lower()
            # Normalize source names
            if 'naukri' in source:
                source = 'naukri'
            elif 'linkedin' in source:
                source = 'linkedin'
            elif 'stackoverflow' in source:
                source = 'stackoverflow'
            elif 'github' in source:
                source = 'github'
            
            if source in by_source:
                by_source[source].append(match)
        
        # Log distribution
        for source, matches in by_source.items():
            logger.info(f"   {source}: {len(matches)} candidates")
        
        # Calculate how many to take from each source
        available_sources = [s for s in sources if by_source[s]]
        if not available_sources:
            return matched_candidates[:max_results]
        
        per_source = max(1, max_results // len(available_sources))  # At least 1 per source
        remainder = max_results % len(available_sources)
        
        logger.info(f"   Taking {per_source} from each source (+{remainder} extra)")
        
        # Take top candidates from each source
        balanced = []
        for i, source in enumerate(available_sources):
            # Take per_source + 1 for first 'remainder' sources, but at least 1
            take = max(1, per_source + (1 if i < remainder else 0))
            balanced.extend(by_source[source][:take])
        
        # Sort by score and limit to max_results
        balanced.sort(key=lambda x: x['combined_score'], reverse=True)
        balanced = balanced[:max_results]
        
        # Log final distribution
        final_dist = {}
        for match in balanced:
            source = match['candidate'].source_portal
            final_dist[source] = final_dist.get(source, 0) + 1
        
        logger.info(f"✅ Final balanced distribution: {final_dist}")
        
        return balanced
