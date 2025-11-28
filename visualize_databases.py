#!/usr/bin/env python3
"""
Database Visualization Tool
Shows Vector DB and NoSQL DB statistics with detailed breakdowns
"""
from src.vector_db import CandidateVectorDB
from src.nosql_db import NoSQLJobDB
from collections import Counter
import json

def visualize_vector_db():
    """Visualize Vector Database"""
    print("\n" + "="*100)
    print(" "*35 + "VECTOR DATABASE (ChromaDB)")
    print("="*100)
    
    try:
        vector_db = CandidateVectorDB()
        results = vector_db.collection.get()
        
        total = len(results['ids'])
        print(f"\n📊 Total Candidates: {total}")
        
        if total == 0:
            print("   ⚠️  Database is empty!")
            return
        
        # Group by source
        by_source = Counter()
        by_title = Counter()
        all_skills = []
        
        for metadata in results['metadatas']:
            source = metadata.get('source_portal') or metadata.get('source', 'unknown')
            title = metadata.get('title', 'N/A')
            skills_str = metadata.get('skills', '[]')
            
            by_source[source] += 1
            by_title[title] += 1
            
            # Parse skills
            try:
                if isinstance(skills_str, str):
                    skills = json.loads(skills_str)
                else:
                    skills = skills_str
                all_skills.extend(skills)
            except:
                pass
        
        # Show by source
        print(f"\n📍 By Source Portal:")
        for source, count in by_source.most_common():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            print(f"   {source:20s} {count:4d} ({percentage:5.1f}%) {bar}")
        
        # Show top titles
        print(f"\n💼 Top 10 Job Titles:")
        for title, count in by_title.most_common(10):
            print(f"   {count:3d}x {title[:70]}")
        
        # Show top skills
        if all_skills:
            skill_counts = Counter(all_skills)
            print(f"\n🎯 Top 15 Skills:")
            for skill, count in skill_counts.most_common(15):
                percentage = (count / total) * 100
                print(f"   {skill:20s} {count:4d} candidates ({percentage:5.1f}%)")
        
        # Show sample candidates
        print(f"\n👥 Sample Candidates (first 5):")
        for i in range(min(5, total)):
            metadata = results['metadatas'][i]
            name = metadata.get('name', 'Unknown')
            title = metadata.get('title', 'N/A')
            source = metadata.get('source_portal') or metadata.get('source', 'unknown')
            print(f"   {i+1}. {name} - {title[:50]} (from {source})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def visualize_nosql_db():
    """Visualize NoSQL Database"""
    print("\n" + "="*100)
    print(" "*35 + "NOSQL DATABASE (JSON Files)")
    print("="*100)
    
    try:
        nosql_db = NoSQLJobDB()
        jobs = nosql_db.get_all_jobs()
        
        print(f"\n📊 Total Jobs: {len(jobs)}")
        
        if not jobs:
            print("   ⚠️  No jobs found!")
            return
        
        # Statistics
        total_candidates = 0
        by_status = Counter()
        by_title = Counter()
        
        for job in jobs:
            status = job.status.value if hasattr(job.status, 'value') else str(job.status)
            by_status[status] += 1
            by_title[job.description.title] += 1
            total_candidates += len(job.candidates)
        
        print(f"📊 Total Candidates Matched: {total_candidates}")
        print(f"📊 Average Candidates per Job: {total_candidates / len(jobs):.1f}")
        
        # Show by status
        print(f"\n📈 By Status:")
        for status, count in by_status.most_common():
            print(f"   {status:15s} {count:3d} jobs")
        
        # Show by title
        print(f"\n💼 Job Titles:")
        for title, count in by_title.most_common():
            print(f"   {count:2d}x {title}")
        
        # Show recent jobs
        print(f"\n📋 Recent Jobs (last 5):")
        for i, job in enumerate(jobs[:5], 1):
            candidate_count = len(job.candidates)
            status = job.status.value if hasattr(job.status, 'value') else str(job.status)
            created = job.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(job.created_at, 'strftime') else str(job.created_at)
            
            print(f"\n   {i}. {job.description.title} ({status})")
            print(f"      Created: {created}")
            print(f"      Skills: {', '.join(job.description.required_skills[:5])}")
            print(f"      Experience: {job.description.experience_years} years")
            print(f"      Location: {job.description.location}")
            print(f"      Candidates: {candidate_count}")
            
            if candidate_count > 0:
                # Show top 3 candidates
                print(f"      Top candidates:")
                for j, cand_data in enumerate(job.candidates[:3], 1):
                    cand = cand_data.candidate if hasattr(cand_data, 'candidate') else cand_data
                    score = cand_data.match_score if hasattr(cand_data, 'match_score') else 0
                    print(f"         {j}. {cand.name} ({cand.source_portal}) - Score: {score*100:.0f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def show_database_health():
    """Show overall database health"""
    print("\n" + "="*100)
    print(" "*35 + "DATABASE HEALTH CHECK")
    print("="*100)
    
    try:
        # Vector DB
        vector_db = CandidateVectorDB()
        vector_results = vector_db.collection.get()
        vector_total = len(vector_results['ids'])
        
        # NoSQL DB
        nosql_db = NoSQLJobDB()
        jobs = nosql_db.get_all_jobs()
        nosql_total = len(jobs)
        
        print(f"\n✅ Vector DB: {vector_total} candidates")
        print(f"✅ NoSQL DB: {nosql_total} jobs")
        
        if vector_total > 0 and nosql_total > 0:
            print(f"\n🎉 Both databases are healthy and populated!")
        elif vector_total > 0:
            print(f"\n⚠️  Vector DB has data but no jobs completed yet")
        elif nosql_total > 0:
            print(f"\n⚠️  Jobs exist but Vector DB is empty")
        else:
            print(f"\n⚠️  Both databases are empty - run a job search to populate")
        
        # Check data consistency
        if nosql_total > 0:
            total_matched = sum(len(job.candidates) for job in jobs)
            print(f"\n📊 Data Consistency:")
            print(f"   Scraped candidates: {vector_total}")
            print(f"   Matched candidates: {total_matched}")
            print(f"   Match rate: {(total_matched/vector_total*100) if vector_total > 0 else 0:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "="*100)
    print(" "*30 + "DATABASE VISUALIZATION DASHBOARD")
    print("="*100)
    
    show_database_health()
    visualize_vector_db()
    visualize_nosql_db()
    
    print("\n" + "="*100)
    print(" "*40 + "END OF REPORT")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
