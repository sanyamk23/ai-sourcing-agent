"""Test script for job title and skills expansion"""

import asyncio
from src.config import Config
from src.llm_provider import LLMProvider
from src.job_expander import JobExpander
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_expansion():
    """Test job title and skills expansion"""
    
    # Load config
    config = Config.load_yaml_config()
    
    # Initialize LLM provider and expander
    llm_provider = LLMProvider(config)
    expander = JobExpander(llm_provider)
    
    # Test cases
    test_cases = [
        {
            "title": "Python Developer",
            "skills": ["Python", "Django", "REST API", "PostgreSQL"]
        },
        {
            "title": "Frontend Engineer",
            "skills": ["React", "JavaScript", "CSS", "HTML"]
        },
        {
            "title": "Data Scientist",
            "skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        print(f"\n📋 Original Job Title: {test_case['title']}")
        print(f"📋 Original Skills ({len(test_case['skills'])}): {', '.join(test_case['skills'])}")
        
        # Expand
        result = expander.expand_job_data(
            job_title=test_case['title'],
            skills=test_case['skills']
        )
        
        print(f"\n✨ Expanded Job Titles ({len(result['job_titles'])}):")
        for idx, title in enumerate(result['job_titles'], 1):
            print(f"   {idx}. {title}")
        
        print(f"\n✨ Expanded Skills ({len(result['skills'])}):")
        original_set = set(test_case['skills'])
        new_skills = [s for s in result['skills'] if s not in original_set]
        
        print(f"   Original skills: {', '.join(test_case['skills'])}")
        print(f"   New skills added ({len(new_skills)}): {', '.join(new_skills)}")
        print(f"   Total skills: {len(result['skills'])}")
        print(f"   Expansion rate: {((len(result['skills']) - len(test_case['skills'])) / len(test_case['skills']) * 100):.1f}%")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print(f"\n{'='*80}")
    print("✅ All tests completed!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(test_expansion())
