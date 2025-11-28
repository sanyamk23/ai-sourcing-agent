#!/usr/bin/env python3
"""
Test creating a job via the API
"""
import requests
import json
import time

API_URL = "http://localhost:8000"

# Create a test job
job_data = {
    "title": "Python Developer",
    "description": "Looking for an experienced Python developer with Django and React skills",
    "required_skills": ["Python", "Django", "React"],
    "experience_years": 3,
    "location": "Remote"
}

print("\n" + "="*80)
print("TESTING JOB CREATION")
print("="*80)

print("\n1. Creating job...")
print(f"   Job: {job_data['title']}")
print(f"   Skills: {', '.join(job_data['required_skills'])}")
print(f"   Experience: {job_data['experience_years']} years")

try:
    response = requests.post(f"{API_URL}/jobs", json=job_data)
    
    if response.status_code == 200:
        job = response.json()
        job_id = job['id']
        print(f"\n✅ Job created successfully!")
        print(f"   Job ID: {job_id}")
        print(f"   Status: {job['status']}")
        
        print("\n2. Polling for results...")
        max_attempts = 60
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)
            attempt += 1
            
            status_response = requests.get(f"{API_URL}/jobs/{job_id}")
            if status_response.status_code == 200:
                job_status = status_response.json()
                status = job_status['status']
                candidate_count = len(job_status.get('candidates', []))
                
                print(f"   Attempt {attempt}: Status={status}, Candidates={candidate_count}")
                
                if status == 'completed':
                    print(f"\n✅ Job completed!")
                    print(f"   Total candidates: {candidate_count}")
                    
                    if candidate_count > 0:
                        print(f"\n📊 Top candidates:")
                        for i, cand_data in enumerate(job_status['candidates'][:5], 1):
                            cand = cand_data.get('candidate', cand_data)
                            match_score = cand_data.get('match_score', 0)
                            match_breakdown = cand_data.get('match_breakdown', {})
                            
                            print(f"\n   {i}. {cand['name']} ({cand['source_portal']})")
                            print(f"      Title: {cand['current_title']}")
                            print(f"      Match Score: {match_score*100:.0f}%")
                            
                            if match_breakdown:
                                matched_skills = match_breakdown.get('matched_skills', [])
                                missing_skills = match_breakdown.get('missing_skills', [])
                                print(f"      Matched Skills: {', '.join(matched_skills)}")
                                if missing_skills:
                                    print(f"      Missing Skills: {', '.join(missing_skills)}")
                    
                    break
                elif status == 'failed':
                    print(f"\n❌ Job failed!")
                    break
        
        if attempt >= max_attempts:
            print(f"\n⏱️  Timeout waiting for job completion")
    else:
        print(f"\n❌ Error creating job: {response.status_code}")
        print(f"   {response.text}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
