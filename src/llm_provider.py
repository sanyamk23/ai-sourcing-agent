"""LLM Provider abstraction to support both Groq and OpenAI"""

import os
from typing import List, Optional
from groq import Groq
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    """Unified interface for LLM providers (Groq, OpenAI)"""
    
    def __init__(self, config: dict):
        self.config = config
        self.provider = config['llm'].get('provider', 'groq')
        
        # Initialize LLM client
        if self.provider == 'groq':
            groq_key = os.getenv('GROQ_API_KEY') or config['llm'].get('groq_api_key')
            if not groq_key:
                raise ValueError("GROQ_API_KEY not found in environment or config")
            self.client = Groq(api_key=groq_key)
            self.model = config['llm'].get('groq_model', 'llama-3.3-70b-versatile')
            logger.info(f"Using Groq with model: {self.model}")
        else:
            openai_key = os.getenv('OPENAI_API_KEY') or config['llm'].get('openai_api_key')
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not found in environment or config")
            self.client = OpenAI(api_key=openai_key)
            self.model = config['llm'].get('openai_model', 'gpt-4')
            logger.info(f"Using OpenAI with model: {self.model}")
        
        # Initialize embedding model
        embedding_model = config['llm'].get('embedding_model', 'sentence-transformers')
        if embedding_model == 'sentence-transformers':
            logger.info("Loading local sentence-transformers model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_local_embeddings = True
            logger.info("Local embeddings ready (free, no API calls)")
        else:
            self.use_local_embeddings = False
            logger.info("Using OpenAI embeddings")
    
    def chat_completion(self, messages: List[dict], max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Get chat completion from LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        if self.use_local_embeddings:
            # Use local sentence-transformers (free, no API calls)
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        else:
            # Use OpenAI embeddings
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts (more efficient)"""
        if self.use_local_embeddings:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() for emb in embeddings]
        else:
            # OpenAI batch embeddings
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
