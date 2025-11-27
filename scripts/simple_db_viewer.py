"""
Simple Database Viewer - No external dependencies
View MongoDB and ChromaDB databases
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nosql_database import mongo_db
from src.vector_database import vector_db
import json


def print_header(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def view_mongodb():
    """View MongoDB collections"""
    print_header("📊 MongoDB Database")
    
    # Candidates
    candidates = mongo_db.get_all_candidates()
    print(f"✓ Candidates Collection: {len(candidates)} documents\n")
    
    if candidates:
        print("Candidates:")
        print("-" * 100)
        print(f"{'Name':<25} {'Title':<30} {'Experience':<12} {'Location':<20} {'Source':<15}")
        print("-" * 100)
        
        for candidate in candidates[:10]:
            name = candidate.get('name', 'N/A')[:24]
            title = candidate.get('current_title', 'N/A')[:29]
            exp = f"{candidate.get('experience_years', 0)} years"
            location = candidate.get('location', 'N/A')[:19]
            source = candidate.get('source_portal', 'N/A')[:14]
            
            print(f"{name:<25} {title:<30} {exp:<12} {location:<20} {source:<15}")
        
        if len(candidates) > 10:
            print(f"\n... and {len(candidates) - 10} more")
    
    # Jobs
    print("\n")
    jobs = mongo_db.get_all_jobs()
    print(f"✓ Jobs Collection: {len(jobs)} documents\n")
    
    if jobs:
        print("Jobs:")
        print("-" * 100)
        print(f"{'Title':<35} {'Location':<20} {'Experience':<12} {'Candidates':<12} {'Status':<15}")
        print("-" * 100)
        
        for job in jobs[:10]:
            title = job.get('title', 'N/A')[:34]
            location = job.get('location', 'N/A')[:19]
            exp = f"{job.get('experience_years', 0)}+ years"
            candidates_count = len(job.get('candidates', []))
            status = job.get('status', 'N/A')[:14]
            
            print(f"{title:<35} {location:<20} {exp:<12} {candidates_count:<12} {status:<15}")
    
    # Scraped candidates
    print("\n")
    scraped = mongo_db.get_scraped_candidates()
    print(f"✓ Scraped Candidates Collection: {len(scraped)} documents")


def view_chromadb():
    """View ChromaDB collections"""
    print_header("🔮 ChromaDB Vector Database")
    
    # Final candidates
    final_count = vector_db.get_collection_count(is_final=True)
    print(f"✓ Final Candidates Collection: {final_count} embeddings")
    
    # Scraped candidates
    scraped_count = vector_db.get_collection_count(is_final=False)
    print(f"✓ Scraped Candidates Collection: {scraped_count} embeddings")
    
    # Show sample embeddings
    if final_count > 0:
        print("\nSample Candidates with Embeddings:")
        print("-" * 100)
        print(f"{'Name':<25} {'Title':<35} {'Location':<20} {'Has Embedding':<15}")
        print("-" * 100)
        
        results = vector_db.semantic_search("developer", n_results=5, is_final=True)
        
        for result in results:
            metadata = result.get('metadata', {})
            name = metadata.get('name', 'N/A')[:24]
            title = metadata.get('title', 'N/A')[:34]
            location = metadata.get('location', 'N/A')[:19]
            
            print(f"{name:<25} {title:<35} {location:<20} {'✓ Yes':<15}")


def test_semantic_search():
    """Test semantic search functionality"""
    print_header("🔍 Testing Semantic Search")
    
    queries = [
        "Python developer with AWS experience",
        "Data engineer with Spark and SQL",
        "Senior software engineer"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 100)
        
        results = vector_db.semantic_search(query, n_results=3, is_final=True)
        
        if results:
            print(f"{'Rank':<6} {'Name':<25} {'Title':<35} {'Similarity':<15}")
            print("-" * 100)
            
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                distance = result.get('distance', 0)
                similarity = f"{(1 - distance) * 100:.1f}%" if distance else "N/A"
                
                name = metadata.get('name', 'N/A')[:24]
                title = metadata.get('title', 'N/A')[:34]
                
                print(f"{i:<6} {name:<25} {title:<35} {similarity:<15}")
        else:
            print("No results found")


def view_candidate_detail():
    """View detailed candidate information"""
    print_header("👤 Candidate Details")
    
    # Get first candidate
    candidates = mongo_db.get_all_candidates()
    if not candidates:
        print("No candidates found")
        return
    
    candidate = candidates[0]
    
    print(f"Name:       {candidate.get('name', 'N/A')}")
    print(f"Title:      {candidate.get('current_title', 'N/A')}")
    print(f"Email:      {candidate.get('email', 'N/A')}")
    print(f"Phone:      {candidate.get('phone', 'N/A')}")
    print(f"Experience: {candidate.get('experience_years', 0)} years")
    print(f"Location:   {candidate.get('location', 'N/A')}")
    print(f"Source:     {candidate.get('source_portal', 'N/A')}")
    print(f"Profile:    {candidate.get('profile_url', 'N/A')}")
    
    skills = candidate.get('skills', [])
    if skills:
        print(f"\nSkills ({len(skills)}):")
        print("  " + ", ".join(skills[:15]))
        if len(skills) > 15:
            print(f"  ... and {len(skills) - 15} more")
    
    summary = candidate.get('summary', '')
    if summary:
        print(f"\nSummary:")
        print("  " + summary[:200] + "...")
    
    # Check vector DB
    vector_candidate = vector_db.get_candidate_by_id(candidate['id'], is_final=True)
    if vector_candidate:
        print(f"\n✓ Vector embedding exists in ChromaDB")
    else:
        print(f"\n✗ No vector embedding found")


def show_statistics():
    """Show database statistics"""
    print_header("📈 Database Statistics")
    
    # MongoDB stats
    candidates = mongo_db.get_all_candidates()
    jobs = mongo_db.get_all_jobs()
    scraped = mongo_db.get_scraped_candidates()
    
    # ChromaDB stats
    final_vectors = vector_db.get_collection_count(is_final=True)
    scraped_vectors = vector_db.get_collection_count(is_final=False)
    
    print(f"{'Database':<15} {'Collection':<25} {'Count':<10}")
    print("-" * 50)
    print(f"{'MongoDB':<15} {'Candidates':<25} {len(candidates):<10}")
    print(f"{'MongoDB':<15} {'Jobs':<25} {len(jobs):<10}")
    print(f"{'MongoDB':<15} {'Scraped Candidates':<25} {len(scraped):<10}")
    print(f"{'ChromaDB':<15} {'Final Embeddings':<25} {final_vectors:<10}")
    print(f"{'ChromaDB':<15} {'Scraped Embeddings':<25} {scraped_vectors:<10}")
    
    # Calculate insights
    if candidates:
        total_exp = sum(c.get('experience_years', 0) for c in candidates)
        avg_exp = total_exp / len(candidates)
        
        sources = {}
        for c in candidates:
            source = c.get('source_portal', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\nInsights:")
        print(f"  • Average Experience: {avg_exp:.1f} years")
        print(f"  • Sources: {', '.join([f'{k}: {v}' for k, v in sources.items()])}")


def main_menu():
    """Interactive menu"""
    while True:
        print("\n" + "="*60)
        print("   Database Viewer - MongoDB + ChromaDB")
        print("="*60)
        print("\n[1] View MongoDB Collections")
        print("[2] View ChromaDB Vector Database")
        print("[3] Test Semantic Search")
        print("[4] View Candidate Details")
        print("[5] Show Statistics")
        print("[6] View All")
        print("[0] Exit\n")
        
        choice = input("Select option: ").strip()
        
        if choice == "1":
            view_mongodb()
        elif choice == "2":
            view_chromadb()
        elif choice == "3":
            test_semantic_search()
        elif choice == "4":
            view_candidate_detail()
        elif choice == "5":
            show_statistics()
        elif choice == "6":
            show_statistics()
            view_mongodb()
            view_chromadb()
            test_semantic_search()
        elif choice == "0":
            print("\nGoodbye! 👋\n")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
