"""
Vector Database using ChromaDB for semantic search and embeddings
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import hashlib
import json
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class VectorDBManager:
    """ChromaDB manager for candidate embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB with persistence (using PersistentClient)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info(f"ChromaDB initialized with persistence at: {persist_directory}")
        
        # Collections
        self.candidates_collection = self.client.get_or_create_collection(
            name="candidates",
            metadata={"description": "Final selected candidates"}
        )
        
        self.scraped_collection = self.client.get_or_create_collection(
            name="scraped_candidates",
            metadata={"description": "All scraped candidates before filtering"}
        )
        
        logger.info("ChromaDB initialized with embedding model")
    
    def _create_candidate_text(self, candidate: Dict) -> str:
        """Create searchable text from candidate data"""
        parts = []
        
        if candidate.get('name'):
            parts.append(f"Name: {candidate['name']}")
        if candidate.get('current_title'):
            parts.append(f"Title: {candidate['current_title']}")
        if candidate.get('summary'):
            parts.append(f"Summary: {candidate['summary']}")
        if candidate.get('skills'):
            skills = candidate['skills'] if isinstance(candidate['skills'], list) else []
            parts.append(f"Skills: {', '.join(skills)}")
        if candidate.get('location'):
            parts.append(f"Location: {candidate['location']}")
        if candidate.get('education'):
            parts.append(f"Education: {candidate['education']}")
        
        return " | ".join(parts)
    
    def _generate_id(self, candidate: Dict) -> str:
        """Generate unique ID for candidate"""
        if candidate.get('id'):
            return candidate['id']
        
        # Generate from profile URL or email
        unique_str = candidate.get('profile_url') or candidate.get('email') or candidate.get('name', '')
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def add_candidate(self, candidate: Dict, is_final: bool = True) -> str:
        """Add candidate to vector database"""
        try:
            candidate_id = self._generate_id(candidate)
            candidate_text = self._create_candidate_text(candidate)
            
            # Choose collection
            collection = self.candidates_collection if is_final else self.scraped_collection
            
            # Add to ChromaDB
            collection.upsert(
                ids=[candidate_id],
                documents=[candidate_text],
                metadatas=[{
                    'name': candidate.get('name', ''),
                    'title': candidate.get('current_title', ''),
                    'location': candidate.get('location', ''),
                    'source': candidate.get('source_portal', ''),
                    'experience_years': candidate.get('experience_years', 0),
                    'profile_url': candidate.get('profile_url', ''),
                    'is_final': is_final
                }]
            )
            
            logger.info(f"Added candidate {candidate_id} to {'final' if is_final else 'scraped'} collection")
            return candidate_id
            
        except Exception as e:
            logger.error(f"Error adding candidate to vector DB: {e}")
            return ""
    
    def add_candidates_batch(self, candidates: List[Dict], is_final: bool = True) -> List[str]:
        """Add multiple candidates at once"""
        ids = []
        documents = []
        metadatas = []
        
        for candidate in candidates:
            candidate_id = self._generate_id(candidate)
            candidate_text = self._create_candidate_text(candidate)
            
            ids.append(candidate_id)
            documents.append(candidate_text)
            metadatas.append({
                'name': candidate.get('name', ''),
                'title': candidate.get('current_title', ''),
                'location': candidate.get('location', ''),
                'source': candidate.get('source_portal', ''),
                'experience_years': candidate.get('experience_years', 0),
                'profile_url': candidate.get('profile_url', ''),
                'is_final': is_final
            })
        
        collection = self.candidates_collection if is_final else self.scraped_collection
        
        try:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} candidates to vector DB")
            return ids
        except Exception as e:
            logger.error(f"Error adding candidates batch: {e}")
            return []
    
    def semantic_search(self, query: str, n_results: int = 10, is_final: bool = True) -> List[Dict]:
        """Search candidates using semantic similarity"""
        try:
            collection = self.candidates_collection if is_final else self.scraped_collection
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            candidates = []
            if results['ids'] and len(results['ids']) > 0:
                for i, candidate_id in enumerate(results['ids'][0]):
                    candidates.append({
                        'id': candidate_id,
                        'metadata': results['metadatas'][0][i],
                        'document': results['documents'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def search_by_job(self, job_description: Dict, n_results: int = 20) -> List[Dict]:
        """Search candidates matching a job description"""
        # Create search query from job
        query_parts = []
        
        if job_description.get('title'):
            query_parts.append(job_description['title'])
        if job_description.get('description'):
            query_parts.append(job_description['description'])
        if job_description.get('required_skills'):
            skills = job_description['required_skills']
            if isinstance(skills, list):
                query_parts.append(' '.join(skills))
        
        query = ' '.join(query_parts)
        
        # Search in scraped collection first (larger pool)
        scraped_results = self.semantic_search(query, n_results=n_results, is_final=False)
        
        return scraped_results
    
    def get_candidate_by_id(self, candidate_id: str, is_final: bool = True) -> Optional[Dict]:
        """Get candidate by ID"""
        try:
            collection = self.candidates_collection if is_final else self.scraped_collection
            
            result = collection.get(
                ids=[candidate_id]
            )
            
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'metadata': result['metadatas'][0],
                    'document': result['documents'][0]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting candidate: {e}")
            return None
    
    def delete_candidate(self, candidate_id: str, is_final: bool = True):
        """Delete candidate from vector DB"""
        try:
            collection = self.candidates_collection if is_final else self.scraped_collection
            collection.delete(ids=[candidate_id])
            logger.info(f"Deleted candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Error deleting candidate: {e}")
    
    def get_collection_count(self, is_final: bool = True) -> int:
        """Get count of candidates in collection"""
        try:
            collection = self.candidates_collection if is_final else self.scraped_collection
            return collection.count()
        except:
            return 0


# Global instance
vector_db = VectorDBManager()
