import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"

# Example job description
job_description = {
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer with expertise in AI/ML and web development.",
    "required_skills": ["Python", "FastAPI", "Machine Learning", "Docker", "PostgreSQL"],
    "experience_years": 5,
    "location": "San Francisco, CA"
}

# Submit job
print("Submitting job description...")
response = requests.post(f"{BASE_URL}/jobs", json=job_description)
job = response.json()
job_id = job['id']
print(f"Job created with ID: {job_id}")
print(f"Status: {job['status']}")

# Poll for completion
print("\nWaiting for candidate sourcing to complete...")
while True:
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    job = response.json()
    status = job['status']
    print(f"Status: {status}")
    
    if status == "completed":
        break
    elif status == "failed":
        print("Job failed!")
        exit(1)
    
    time.sleep(5)

# Get candidates
print("\nFetching top candidates...")
response = requests.get(f"{BASE_URL}/jobs/{job_id}/candidates")
candidates = response.json()

print(f"\nFound {len(candidates)} top candidates:\n")
for i, ranked_candidate in enumerate(candidates[:5], 1):
    candidate = ranked_candidate['candidate']
    score = ranked_candidate['match_score']
    reasoning = ranked_candidate['reasoning']
    
    print(f"{i}. {candidate['name']} (Score: {score:.2f})")
    print(f"   Title: {candidate['current_title']}")
    print(f"   Skills: {', '.join(candidate['skills'])}")
    print(f"   Experience: {candidate['experience_years']} years")
    print(f"   Source: {candidate['source_portal']}")
    print(f"   Reasoning: {reasoning}")
    print()
