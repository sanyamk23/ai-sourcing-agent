from typing import List
import numpy as np
from src.models import Candidate, JobDescription
from src.llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class CandidateMatcher:
    """Matches candidates to job descriptions using embeddings"""
    
    def __init__(self, config: dict):
        self.config = config
        self.llm_provider = LLMProvider(config)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        return self.llm_provider.get_embedding(text)
    
    def _candidate_to_text(self, candidate: Candidate) -> str:
        """Convert candidate to text representation"""
        parts = [
            f"Title: {candidate.current_title or 'N/A'}",
            f"Skills: {', '.join(candidate.skills)}",
            f"Experience: {candidate.experience_years or 0} years",
            f"Education: {candidate.education or 'N/A'}",
            f"Location: {candidate.location or 'N/A'}"
        ]
        if candidate.summary:
            parts.append(f"Summary: {candidate.summary}")
        return " | ".join(parts)
    
    def _job_to_text(self, job: JobDescription) -> str:
        """Convert job description to text"""
        parts = [
            f"Title: {job.title}",
            f"Description: {job.description}",
            f"Required Skills: {', '.join(job.required_skills)}",
            f"Experience: {job.experience_years or 0} years",
            f"Location: {job.location or 'Any'}"
        ]
        return " | ".join(parts)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
    
    def match_candidates(self, job: JobDescription, candidates: List[Candidate], threshold: float = 0.6) -> List[Candidate]:
        """Match candidates to job description"""
        logger.info(f"Matching {len(candidates)} candidates to job")
        
        job_text = self._job_to_text(job)
        job_embedding = self._get_embedding(job_text)
        
        matched = []
        for candidate in candidates:
            candidate_text = self._candidate_to_text(candidate)
            candidate_embedding = self._get_embedding(candidate_text)
            
            similarity = self._cosine_similarity(job_embedding, candidate_embedding)
            
            if similarity >= threshold:
                matched.append(candidate)
        
        logger.info(f"Matched {len(matched)} candidates above threshold {threshold}")
        return matched
