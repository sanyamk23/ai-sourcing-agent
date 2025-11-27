from typing import List, Dict
from src.models import Candidate, JobDescription, RankedCandidate
from src.llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class CandidateRanker:
    """Ranks candidates based on multiple factors"""
    
    def __init__(self, config: dict):
        self.config = config
        self.weights = config['ranking']['weights']
        self.llm_provider = LLMProvider(config)
    
    def _calculate_skills_match(self, job: JobDescription, candidate: Candidate) -> float:
        """Calculate skills match score"""
        if not job.required_skills or not candidate.skills:
            return 0.0
        
        required = set(s.lower() for s in job.required_skills)
        candidate_skills = set(s.lower() for s in candidate.skills)
        
        matched = required.intersection(candidate_skills)
        return len(matched) / len(required) if required else 0.0
    
    def _calculate_experience_match(self, job: JobDescription, candidate: Candidate) -> float:
        """Calculate experience match score"""
        if not job.experience_years or not candidate.experience_years:
            return 0.5
        
        diff = abs(job.experience_years - candidate.experience_years)
        if diff == 0:
            return 1.0
        elif diff <= 2:
            return 0.8
        elif diff <= 5:
            return 0.5
        else:
            return 0.2
    
    def _calculate_location_match(self, job: JobDescription, candidate: Candidate) -> float:
        """Calculate location match score"""
        if not job.location or not candidate.location:
            return 0.5
        
        return 1.0 if job.location.lower() in candidate.location.lower() else 0.3
    
    def _get_ai_reasoning(self, job: JobDescription, candidate: Candidate, scores: Dict[str, float]) -> str:
        """Get AI-generated reasoning for the match"""
        prompt = f"""Analyze this candidate match:

Job: {job.title}
Required Skills: {', '.join(job.required_skills)}
Experience: {job.experience_years} years

Candidate: {candidate.name}
Skills: {', '.join(candidate.skills)}
Experience: {candidate.experience_years} years

Match Scores:
- Skills: {scores['skills_match']:.2f}
- Experience: {scores['experience_match']:.2f}
- Location: {scores['location_match']:.2f}

Provide a brief 2-3 sentence reasoning for this match."""

        messages = [{"role": "user", "content": prompt}]
        return self.llm_provider.chat_completion(messages, max_tokens=150)
    
    def rank_candidates(self, job: JobDescription, candidates: List[Candidate], top_n: int = 20) -> List[RankedCandidate]:
        """Rank candidates and return top N"""
        logger.info(f"Ranking {len(candidates)} candidates")
        
        ranked = []
        for candidate in candidates:
            scores = {
                'skills_match': self._calculate_skills_match(job, candidate),
                'experience_match': self._calculate_experience_match(job, candidate),
                'location_match': self._calculate_location_match(job, candidate),
                'education_match': 0.7,  # Simplified
                'availability': 0.8  # Simplified
            }
            
            # Calculate weighted score
            total_score = sum(scores[k] * self.weights[k] for k in scores.keys())
            
            # Get AI reasoning
            reasoning = self._get_ai_reasoning(job, candidate, scores)
            
            ranked_candidate = RankedCandidate(
                candidate=candidate,
                match_score=total_score,
                match_breakdown=scores,
                reasoning=reasoning
            )
            ranked.append(ranked_candidate)
        
        # Sort by score descending
        ranked.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"Returning top {top_n} candidates")
        return ranked[:top_n]
