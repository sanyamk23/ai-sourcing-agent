"""
View and explore MongoDB and ChromaDB databases
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nosql_database import mongo_db
from src.vector_database import vector_db
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import json

console = Console()


def view_mongodb():
    """View MongoDB collections"""
    console.print("\n[bold cyan]📊 MongoDB Database[/bold cyan]\n")
    
    # Candidates
    candidates = mongo_db.get_all_candidates()
    console.print(f"[green]✓[/green] Candidates Collection: {len(candidates)} documents")
    
    if candidates:
        table = Table(title="Candidates", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Skills", style="yellow")
        table.add_column("Experience", style="magenta")
        table.add_column("Location", style="blue")
        table.add_column("Source", style="red")
        
        for candidate in candidates[:10]:  # Show first 10
            skills = candidate.get('skills', [])
            if isinstance(skills, list):
                skills_str = ', '.join(skills[:3])
                if len(skills) > 3:
                    skills_str += f" +{len(skills)-3}"
            else:
                skills_str = str(skills)[:30]
            
            table.add_row(
                candidate.get('name', 'N/A')[:30],
                candidate.get('current_title', 'N/A')[:30],
                skills_str,
                f"{candidate.get('experience_years', 0)} yrs",
                candidate.get('location', 'N/A')[:20],
                candidate.get('source_portal', 'N/A')
            )
        
        console.print(table)
    
    # Jobs
    jobs = mongo_db.get_all_jobs()
    console.print(f"\n[green]✓[/green] Jobs Collection: {len(jobs)} documents")
    
    if jobs:
        table = Table(title="Jobs", box=box.ROUNDED)
        table.add_column("Title", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Experience", style="yellow")
        table.add_column("Candidates", style="magenta")
        table.add_column("Status", style="blue")
        table.add_column("Created", style="white")
        
        for job in jobs[:10]:
            candidates_count = len(job.get('candidates', []))
            table.add_row(
                job.get('title', 'N/A')[:40],
                job.get('location', 'N/A')[:20],
                f"{job.get('experience_years', 0)}+ yrs",
                str(candidates_count),
                job.get('status', 'N/A'),
                str(job.get('created_at', ''))[:10]
            )
        
        console.print(table)
    
    # Scraped candidates
    scraped = mongo_db.get_scraped_candidates()
    console.print(f"\n[green]✓[/green] Scraped Candidates Collection: {len(scraped)} documents")


def view_chromadb():
    """View ChromaDB collections"""
    console.print("\n[bold cyan]🔮 ChromaDB Vector Database[/bold cyan]\n")
    
    # Final candidates
    final_count = vector_db.get_collection_count(is_final=True)
    console.print(f"[green]✓[/green] Final Candidates Collection: {final_count} embeddings")
    
    # Scraped candidates
    scraped_count = vector_db.get_collection_count(is_final=False)
    console.print(f"[green]✓[/green] Scraped Candidates Collection: {scraped_count} embeddings")
    
    # Show sample embeddings
    if final_count > 0:
        console.print("\n[yellow]Sample Candidates with Embeddings:[/yellow]")
        
        # Get a few candidates
        results = vector_db.semantic_search("developer", n_results=5, is_final=True)
        
        table = Table(title="Vector Embeddings", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Title", style="yellow")
        table.add_column("Location", style="blue")
        table.add_column("Has Embedding", style="magenta")
        
        for result in results:
            metadata = result.get('metadata', {})
            table.add_row(
                result.get('id', '')[:20],
                metadata.get('name', 'N/A')[:25],
                metadata.get('title', 'N/A')[:30],
                metadata.get('location', 'N/A')[:20],
                "✓ Yes"
            )
        
        console.print(table)


def test_semantic_search():
    """Test semantic search functionality"""
    console.print("\n[bold cyan]🔍 Testing Semantic Search[/bold cyan]\n")
    
    queries = [
        "Python developer with AWS experience",
        "Data engineer with Spark and SQL",
        "Senior software engineer"
    ]
    
    for query in queries:
        console.print(f"\n[yellow]Query:[/yellow] '{query}'")
        results = vector_db.semantic_search(query, n_results=3, is_final=True)
        
        if results:
            table = Table(box=box.SIMPLE)
            table.add_column("Rank", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Title", style="yellow")
            table.add_column("Similarity", style="magenta")
            
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                distance = result.get('distance', 0)
                similarity = f"{(1 - distance) * 100:.1f}%" if distance else "N/A"
                
                table.add_row(
                    str(i),
                    metadata.get('name', 'N/A')[:30],
                    metadata.get('title', 'N/A')[:40],
                    similarity
                )
            
            console.print(table)
        else:
            console.print("[red]No results found[/red]")


def view_candidate_detail(candidate_id: str = None):
    """View detailed candidate information"""
    if not candidate_id:
        # Get first candidate
        candidates = mongo_db.get_all_candidates()
        if not candidates:
            console.print("[red]No candidates found[/red]")
            return
        candidate_id = candidates[0]['id']
    
    console.print(f"\n[bold cyan]👤 Candidate Details[/bold cyan]\n")
    
    # Get from MongoDB
    candidate = mongo_db.get_candidate(candidate_id)
    
    if candidate:
        # Create panel with candidate info
        info = f"""
[cyan]Name:[/cyan] {candidate.get('name', 'N/A')}
[cyan]Title:[/cyan] {candidate.get('current_title', 'N/A')}
[cyan]Email:[/cyan] {candidate.get('email', 'N/A')}
[cyan]Phone:[/cyan] {candidate.get('phone', 'N/A')}
[cyan]Experience:[/cyan] {candidate.get('experience_years', 0)} years
[cyan]Location:[/cyan] {candidate.get('location', 'N/A')}
[cyan]Source:[/cyan] {candidate.get('source_portal', 'N/A')}
[cyan]Profile:[/cyan] {candidate.get('profile_url', 'N/A')}

[yellow]Skills:[/yellow]
{', '.join(candidate.get('skills', [])[:10])}

[yellow]Summary:[/yellow]
{candidate.get('summary', 'N/A')[:200]}...
        """
        
        panel = Panel(info, title=f"Candidate: {candidate.get('name', 'Unknown')}", border_style="green")
        console.print(panel)
        
        # Get from ChromaDB
        vector_candidate = vector_db.get_candidate_by_id(candidate_id, is_final=True)
        if vector_candidate:
            console.print("\n[green]✓[/green] Vector embedding exists in ChromaDB")
            console.print(f"[dim]Document text: {vector_candidate.get('document', '')[:100]}...[/dim]")
        else:
            console.print("\n[red]✗[/red] No vector embedding found")
    else:
        console.print(f"[red]Candidate {candidate_id} not found[/red]")


def show_statistics():
    """Show database statistics"""
    console.print("\n[bold cyan]📈 Database Statistics[/bold cyan]\n")
    
    # MongoDB stats
    candidates = mongo_db.get_all_candidates()
    jobs = mongo_db.get_all_jobs()
    scraped = mongo_db.get_scraped_candidates()
    
    # ChromaDB stats
    final_vectors = vector_db.get_collection_count(is_final=True)
    scraped_vectors = vector_db.get_collection_count(is_final=False)
    
    stats_table = Table(title="Database Statistics", box=box.DOUBLE)
    stats_table.add_column("Database", style="cyan")
    stats_table.add_column("Collection", style="green")
    stats_table.add_column("Count", style="yellow")
    
    stats_table.add_row("MongoDB", "Candidates", str(len(candidates)))
    stats_table.add_row("MongoDB", "Jobs", str(len(jobs)))
    stats_table.add_row("MongoDB", "Scraped Candidates", str(len(scraped)))
    stats_table.add_row("ChromaDB", "Final Embeddings", str(final_vectors))
    stats_table.add_row("ChromaDB", "Scraped Embeddings", str(scraped_vectors))
    
    console.print(stats_table)
    
    # Calculate some insights
    if candidates:
        total_exp = sum(c.get('experience_years', 0) for c in candidates)
        avg_exp = total_exp / len(candidates)
        
        sources = {}
        for c in candidates:
            source = c.get('source_portal', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        console.print(f"\n[yellow]Insights:[/yellow]")
        console.print(f"  • Average Experience: {avg_exp:.1f} years")
        console.print(f"  • Sources: {', '.join([f'{k}: {v}' for k, v in sources.items()])}")


def main_menu():
    """Interactive menu"""
    while True:
        console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]   Database Viewer - MongoDB + ChromaDB[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        console.print("[1] View MongoDB Collections")
        console.print("[2] View ChromaDB Vector Database")
        console.print("[3] Test Semantic Search")
        console.print("[4] View Candidate Details")
        console.print("[5] Show Statistics")
        console.print("[6] View All")
        console.print("[0] Exit\n")
        
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
            console.print("\n[green]Goodbye! 👋[/green]\n")
            break
        else:
            console.print("[red]Invalid option[/red]")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
