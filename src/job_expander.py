"""Job Title and Skills Expander using LLM"""

import json
import logging
from typing import List, Dict
from src.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class JobExpander:
    """Expands job titles and skills using LLM in a single call"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def expand_job_data(self, job_title: str, skills: List[str]) -> Dict[str, List[str]]:
        """
        Expand job title and skills in a single LLM call.
        
        Args:
            job_title: Original job title (e.g., "Python Developer")
            skills: Original skills list (e.g., ["Python", "Django", "REST API"])
        
        Returns:
            Dictionary with:
                - "job_titles": List of 4-5 related job titles including the original
                - "skills": Expanded skills list (25-30% more skills added)
        """
        logger.info(f"Expanding job data for: {job_title}")
        logger.info(f"Original skills count: {len(skills)}")
        
        # Calculate target skills count (25-30% more)
        # Use 27.5% as the midpoint, but ensure at least 2 skills are added
        additional_skills_count = max(2, int(len(skills) * 0.275))
        
        # Build prompt for single LLM call
        prompt = self._build_expansion_prompt(job_title, skills, additional_skills_count)
        
        try:
            # Make single LLM call
            messages = [
                {
                    "role": "system",
                    "content": "You are a recruitment expert who understands job titles and technical skills. You provide accurate, relevant job market insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm_provider.chat_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.5
            )
            
            # Parse JSON response
            result = self._parse_llm_response(response, job_title, skills)
            
            logger.info(f"✓ Expanded to {len(result['job_titles'])} job titles")
            logger.info(f"✓ Expanded to {len(result['skills'])} total skills (+{len(result['skills']) - len(skills)} new)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error expanding job data: {e}")
            # Return original data if expansion fails
            return {
                "job_titles": [job_title],
                "skills": skills
            }
    
    def _build_expansion_prompt(self, job_title: str, skills: List[str], additional_count: int) -> str:
        """Build the prompt for LLM expansion"""
        skills_str = ", ".join(skills)
        
        prompt = f"""Given the job title "{job_title}" and skills list, expand both in a single response.

**Original Job Title:** {job_title}
**Original Skills:** {skills_str}

**Task 1 - Job Title Variations:**
Generate 4-5 related job titles that are commonly used for similar roles. Include:
- The original title
- Seniority variations (Junior, Senior, Lead, Principal)
- Alternative naming conventions (Developer vs Engineer vs Programmer)
- Specialized variations if applicable

**Task 2 - Skills Expansion:**
Add approximately {additional_count} highly relevant skills to the existing list. These should be:
- Complementary technologies commonly used with the existing skills
- Related frameworks, tools, or methodologies
- Industry-standard skills for this role
- Keep all original skills in the list

**IMPORTANT:** Respond ONLY with valid JSON in this exact format:
{{
  "job_titles": ["title1", "title2", "title3", "title4", "title5"],
  "skills": ["skill1", "skill2", "skill3", ...]
}}

Do not include any explanation, markdown formatting, or additional text. Only the JSON object."""
        
        return prompt
    
    def _parse_llm_response(self, response: str, original_title: str, original_skills: List[str]) -> Dict[str, List[str]]:
        """Parse and validate LLM response"""
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Remove markdown code blocks
                lines = cleaned.split("\n")
                cleaned = "\n".join([line for line in lines if not line.startswith("```")])
            
            # Remove "json" prefix if present
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate structure
            if "job_titles" not in data or "skills" not in data:
                raise ValueError("Missing required keys in response")
            
            # Ensure original title is included
            job_titles = data["job_titles"]
            if original_title not in job_titles:
                job_titles.insert(0, original_title)
            
            # Ensure all original skills are included
            expanded_skills = data["skills"]
            for skill in original_skills:
                if skill not in expanded_skills:
                    expanded_skills.append(skill)
            
            # Remove duplicates while preserving order
            job_titles = list(dict.fromkeys(job_titles))
            expanded_skills = list(dict.fromkeys(expanded_skills))
            
            # Limit to reasonable sizes
            job_titles = job_titles[:5]
            
            return {
                "job_titles": job_titles,
                "skills": expanded_skills
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response}")
            # Return original data
            return {
                "job_titles": [original_title],
                "skills": original_skills
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                "job_titles": [original_title],
                "skills": original_skills
            }
