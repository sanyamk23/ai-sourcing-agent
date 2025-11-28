from typing import List, Set, Dict
import numpy as np
from src.models import Candidate, JobDescription
from src.llm_provider import LLMProvider
import logging
import re

logger = logging.getLogger(__name__)

class CandidateMatcher:
    """Matches candidates to job descriptions using embeddings and keyword matching"""
    
    def __init__(self, config: dict):
        self.config = config
        self.llm_provider = LLMProvider(config)
        
        # Common tech keywords to extract
        self.tech_keywords = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'fastapi', 'spring', 'express',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'git', 'ci/cd', 'jenkins', 'github', 'gitlab',
            'machine learning', 'ai', 'deep learning', 'nlp', 'computer vision',
            'agile', 'scrum', 'devops', 'microservices', 'rest', 'graphql',
            'html', 'css', 'sass', 'webpack', 'babel',
            'testing', 'junit', 'pytest', 'selenium', 'cypress'
        }
    
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
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text"""
        # Convert to lowercase
        text_lower = text.lower()
        
        # Extract all words
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Also extract multi-word phrases
        phrases = []
        for keyword in self.tech_keywords:
            if ' ' in keyword and keyword in text_lower:
                phrases.append(keyword)
        
        # Combine single words and phrases
        keywords = set(words) | set(phrases)
        
        # Filter to only tech keywords
        tech_keywords_found = keywords & self.tech_keywords
        
        return tech_keywords_found
    
    def _extract_job_keywords(self, job: JobDescription) -> Dict[str, Set[str]]:
        """Extract keywords from job description"""
        keywords = {
            'title': self._extract_keywords(job.title),
            'description': self._extract_keywords(job.description),
            'skills': set(skill.lower() for skill in job.required_skills)
        }
        
        # Combine all keywords
        all_keywords = keywords['title'] | keywords['description'] | keywords['skills']
        keywords['all'] = all_keywords
        
        logger.info(f"Extracted {len(all_keywords)} keywords from job: {', '.join(sorted(all_keywords)[:10])}...")
        return keywords
    
    def _calculate_keyword_match(self, job_keywords: Set[str], candidate: Candidate) -> float:
        """Calculate keyword match score between job and candidate"""
        if not job_keywords:
            return 0.5
        
        # Extract candidate keywords
        candidate_text = f"{candidate.current_title or ''} {' '.join(candidate.skills)} {candidate.summary or ''}"
        candidate_keywords = self._extract_keywords(candidate_text)
        
        # Also add explicit skills
        candidate_keywords |= set(skill.lower() for skill in candidate.skills)
        
        # Calculate match
        matched_keywords = job_keywords & candidate_keywords
        match_score = len(matched_keywords) / len(job_keywords) if job_keywords else 0
        
        return match_score
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
    
    def match_candidates(self, job: JobDescription, candidates: List[Candidate], threshold: float = 0.5) -> List[Candidate]:
        """Match candidates to job description using hybrid approach"""
        logger.info(f"Matching {len(candidates)} candidates to job")
        
        # Extract job keywords
        job_keywords_dict = self._extract_job_keywords(job)
        job_keywords = job_keywords_dict['all']
        
        # Get job embedding for semantic matching
        job_text = self._job_to_text(job)
        job_embedding = self._get_embedding(job_text)
        
        matched = []
        for candidate in candidates:
            # 1. Keyword matching (40% weight)
            keyword_score = self._calculate_keyword_match(job_keywords, candidate)
            
            # 2. Semantic matching with embeddings (60% weight)
            candidate_text = self._candidate_to_text(candidate)
            candidate_embedding = self._get_embedding(candidate_text)
            semantic_score = self._cosine_similarity(job_embedding, candidate_embedding)
            
            # 3. Combined score (hybrid approach)
            combined_score = (0.4 * keyword_score) + (0.6 * semantic_score)
            
            # Store scores for ranking
            candidate.keyword_match_score = keyword_score
            candidate.semantic_match_score = semantic_score
            candidate.combined_match_score = combined_score
            
            if combined_score >= threshold:
                matched.append(candidate)
        
        # Sort by combined score
        matched.sort(key=lambda c: c.combined_match_score, reverse=True)
        
        logger.info(f"Matched {len(matched)} candidates above threshold {threshold}")
        logger.info(f"Top candidate scores: {[f'{c.name}: {c.combined_match_score:.2f}' for c in matched[:3]]}")
        return matched
