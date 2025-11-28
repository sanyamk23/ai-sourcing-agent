"""
Vector Database for Candidate Storage and Similarity Search
Uses ChromaDB for local vector storage
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from src.models import Candidate
import logging
import json
import hashlib

logger = logging.getLogger(__name__)

class CandidateVectorDB:
    """Vector database for storing and searching candidates"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """Initialize ChromaDB"""
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="candidates",
            metadata={"description": "Candidate profiles with embeddings"}
        )
        
        logger.info(f"✅ Vector DB initialized: {self.collection.count()} candidates stored")
    
    def _candidate_to_text(self, candidate: Candidate) -> str:
        """Convert candidate to searchable text"""
        parts = [
            f"Name: {candidate.name}",
            f"Title: {candidate.current_title}",
            f"Skills: {', '.join(candidate.skills)}",
            f"Location: {candidate.location}",
        ]
        
        if candidate.summary:
            parts.append(f"Summary: {candidate.summary}")
        
        if candidate.email:
            parts.append(f"Email: {candidate.email}")
        
        return " | ".join(parts)
    
    def add_candidates(self, candidates: List[Candidate]) -> int:
        """Add candidates to vector DB"""
        if not candidates:
            return 0
        
        # Prepare data
        ids = []
        documents = []
        metadatas = []
        
        for candidate in candidates:
            ids.append(candidate.id)
            documents.append(self._candidate_to_text(candidate))
            metadatas.append({
                "name": candidate.name,
                "title": candidate.current_title or "",
                "location": candidate.location or "",
                "source": candidate.source_portal,
                "skills": json.dumps(candidate.skills),
                "profile_url": candidate.profile_url,
                "email": candidate.email or "",
                "summary": candidate.summary or ""
            })
        
        # Add to collection (ChromaDB handles embeddings automatically)
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"✅ Added {len(candidates)} candidates to vector DB")
            return len(candidates)
        except Exception as e:
            logger.error(f"Error adding candidates to vector DB: {e}")
            return 0
    
    def search_similar(self, query: str, n_results: int = 10, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar candidates using vector similarity"""
        try:
            # Build where clause for filtering
            where = None
            if filters:
                where = {}
                if "source" in filters:
                    where["source"] = filters["source"]
                if "location" in filters:
                    where["location"] = {"$contains": filters["location"]}
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None
            )
            
            # Format results
            candidates = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    candidate_data = {
                        "id": results['ids'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None,
                        "metadata": results['metadatas'][0][i],
                        "document": results['documents'][0][i]
                    }
                    candidates.append(candidate_data)
            
            logger.info(f"🔍 Found {len(candidates)} similar candidates for query: '{query[:50]}...'")
            return candidates
            
        except Exception as e:
            logger.error(f"Error searching vector DB: {e}")
            return []
    
    def get_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate by ID"""
        try:
            result = self.collection.get(ids=[candidate_id])
            if result['ids']:
                return {
                    "id": result['ids'][0],
                    "metadata": result['metadatas'][0],
                    "document": result['documents'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting candidate {candidate_id}: {e}")
            return None
    
    def delete_by_source(self, source: str) -> int:
        """Delete all candidates from a specific source"""
        try:
            # Get all IDs from this source
            results = self.collection.get(where={"source": source})
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"🗑️  Deleted {len(results['ids'])} candidates from {source}")
                return len(results['ids'])
            return 0
        except Exception as e:
            logger.error(f"Error deleting candidates from {source}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            total = self.collection.count()
            
            # Get counts by source
            sources = {}
            all_data = self.collection.get()
            if all_data['metadatas']:
                for metadata in all_data['metadatas']:
                    source = metadata.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
            
            return {
                "total_candidates": total,
                "by_source": sources
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_candidates": 0, "by_source": {}}
    
    def clear_all(self):
        """Clear all candidates from database"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("candidates")
            self.collection = self.client.get_or_create_collection(
                name="candidates",
                metadata={"description": "Candidate profiles with embeddings"}
            )
            logger.info("🗑️  Cleared all candidates from vector DB")
        except Exception as e:
            logger.error(f"Error clearing vector DB: {e}")
