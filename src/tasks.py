from celery import Celery
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    'candidate_sourcing',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name='source_candidates')
def source_candidates_task(job_id: str, job_description: dict):
    """Celery task for candidate sourcing"""
    import asyncio
    from src.agent import CandidateSourcingAgent
    from src.models import JobDescription
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    config['llm']['groq_api_key'] = os.getenv('GROQ_API_KEY')
    config['llm']['openai_api_key'] = os.getenv('OPENAI_API_KEY')
    config['linkedin']['username'] = os.getenv('LINKEDIN_USERNAME')
    config['linkedin']['password'] = os.getenv('LINKEDIN_PASSWORD')
    
    # Initialize agent
    agent = CandidateSourcingAgent(config)
    
    # Create job description object
    job_desc = JobDescription(**job_description)
    
    # Run async sourcing
    loop = asyncio.get_event_loop()
    candidates = loop.run_until_complete(agent.source_candidates(job_desc))
    
    return {
        'job_id': job_id,
        'candidates': [c.dict() for c in candidates]
    }
