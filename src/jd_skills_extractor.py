"""
Job Description and Skills Extractor
Extracts and normalizes skills from job descriptions for better matching
"""

import re
from typing import List, Dict, Set
from src.models import JobDescription
import logging

logger = logging.getLogger(__name__)


class JDSkillsExtractor:
    """Extract and normalize skills from job descriptions"""
    
    # Common skill categories and their variations
    SKILL_PATTERNS = {
        # Programming Languages
        'python': ['python', 'python3', 'py', 'python developer', 'senior python'],
        'java': ['java', 'java8', 'java11', 'jdk'],
        'javascript': ['javascript', 'js', 'es6', 'es2015'],
        'typescript': ['typescript', 'ts'],
        'go': ['golang', 'go'],
        'rust': ['rust'],
        'c++': ['c++', 'cpp', 'cplusplus'],
        'c#': ['c#', 'csharp', 'c sharp'],
        'ruby': ['ruby', 'rails', 'ruby on rails'],
        'php': ['php'],
        'swift': ['swift'],
        'kotlin': ['kotlin'],
        'scala': ['scala'],
        
        # Frameworks
        'django': ['django'],
        'flask': ['flask'],
        'fastapi': ['fastapi', 'fast api'],
        'react': ['react', 'reactjs', 'react.js'],
        'angular': ['angular', 'angularjs'],
        'vue': ['vue', 'vuejs', 'vue.js'],
        'node': ['node', 'nodejs', 'node.js'],
        'express': ['express', 'expressjs'],
        'spring': ['spring', 'spring boot', 'springboot'],
        
        # Databases
        'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'mssql', 'oracle'],
        'mongodb': ['mongodb', 'mongo'],
        'redis': ['redis'],
        'elasticsearch': ['elasticsearch', 'elastic search'],
        'cassandra': ['cassandra'],
        
        # Cloud & DevOps
        'aws': ['aws', 'amazon web services'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud', 'google cloud platform'],
        'docker': ['docker', 'containerization'],
        'kubernetes': ['kubernetes', 'k8s'],
        'jenkins': ['jenkins'],
        'terraform': ['terraform'],
        'ansible': ['ansible'],
        
        # Data & ML
        'machine learning': ['machine learning', 'ml', 'deep learning', 'dl'],
        'data science': ['data science', 'data scientist'],
        'pandas': ['pandas'],
        'numpy': ['numpy'],
        'tensorflow': ['tensorflow', 'tf'],
        'pytorch': ['pytorch'],
        'scikit-learn': ['scikit-learn', 'sklearn'],
        
        # Other
        'git': ['git', 'github', 'gitlab', 'version control'],
        'rest api': ['rest', 'restful', 'rest api', 'api'],
        'graphql': ['graphql'],
        'microservices': ['microservices', 'micro services'],
        'agile': ['agile', 'scrum', 'kanban'],
    }
    
    def __init__(self):
        # Build reverse lookup for normalization
        self.skill_normalizer = {}
        for canonical, variations in self.SKILL_PATTERNS.items():
            for variation in variations:
                self.skill_normalizer[variation.lower()] = canonical
    
    def extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract skills from any text"""
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        # Check for each skill variation
        for variation, canonical in self.skill_normalizer.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(canonical)
        
        return found_skills
    
    def extract_from_job_description(self, job_desc: JobDescription) -> Dict[str, any]:
        """Extract comprehensive skill matrix from job description"""
        
        # Combine all text sources
        all_text = f"{job_desc.title} {job_desc.description}"
        if job_desc.required_skills:
            all_text += " " + " ".join(job_desc.required_skills)
        
        # Extract skills from text
        extracted_skills = self.extract_skills_from_text(all_text)
        
        # Add explicitly mentioned required skills
        explicit_skills = set()
        if job_desc.required_skills:
            for skill in job_desc.required_skills:
                normalized = self.skill_normalizer.get(skill.lower(), skill.lower())
                explicit_skills.add(normalized)
        
        # Combine both
        all_skills = extracted_skills.union(explicit_skills)
        
        # Categorize skills
        skill_matrix = {
            'all_skills': list(all_skills),
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_devops': [],
            'data_ml': [],
            'other': []
        }
        
        # Categorize each skill
        for skill in all_skills:
            if skill in ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'scala']:
                skill_matrix['programming_languages'].append(skill)
            elif skill in ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'node', 'express', 'spring']:
                skill_matrix['frameworks'].append(skill)
            elif skill in ['sql', 'mongodb', 'redis', 'elasticsearch', 'cassandra']:
                skill_matrix['databases'].append(skill)
            elif skill in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']:
                skill_matrix['cloud_devops'].append(skill)
            elif skill in ['machine learning', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn']:
                skill_matrix['data_ml'].append(skill)
            else:
                skill_matrix['other'].append(skill)
        
        # Add metadata
        skill_matrix['total_count'] = len(all_skills)
        skill_matrix['experience_years'] = job_desc.experience_years or 0
        skill_matrix['location'] = job_desc.location or ''
        
        logger.info(f"📊 Extracted {len(all_skills)} skills from job description")
        logger.info(f"   Languages: {len(skill_matrix['programming_languages'])}, "
                   f"Frameworks: {len(skill_matrix['frameworks'])}, "
                   f"Databases: {len(skill_matrix['databases'])}")
        
        return skill_matrix
    
    def normalize_candidate_skills(self, candidate_skills: List[str]) -> Set[str]:
        """Normalize candidate skills to match job description format"""
        if not candidate_skills:
            return set()
        
        normalized = set()
        for skill in candidate_skills:
            skill_lower = skill.lower().strip()
            canonical = self.skill_normalizer.get(skill_lower, skill_lower)
            normalized.add(canonical)
        
        return normalized
    
    def calculate_skill_match_score(self, job_skills: Set[str], candidate_skills: Set[str]) -> Dict[str, any]:
        """Calculate detailed skill match score"""
        
        if not job_skills:
            return {
                'score': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'extra_skills': []
            }
        
        # Find matches
        matched = job_skills.intersection(candidate_skills)
        missing = job_skills - candidate_skills
        extra = candidate_skills - job_skills
        
        # Calculate score
        score = len(matched) / len(job_skills) if job_skills else 0.0
        
        return {
            'score': round(score, 2),
            'matched_skills': sorted(list(matched)),
            'missing_skills': sorted(list(missing)),
            'extra_skills': sorted(list(extra)),
            'match_count': len(matched),
            'required_count': len(job_skills)
        }
