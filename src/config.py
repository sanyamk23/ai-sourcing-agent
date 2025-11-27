"""
Centralized configuration management
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_WORKERS = int(os.getenv("API_WORKERS", 1))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # LLM Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LinkedIn Settings
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/candidates.db")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    # Scraping
    SCRAPING_TIMEOUT = int(os.getenv("SCRAPING_TIMEOUT", 300))
    MAX_CONCURRENT_SCRAPERS = int(os.getenv("MAX_CONCURRENT_SCRAPERS", 3))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    @classmethod
    def load_yaml_config(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Replace env variables in config
        if "llm" in config:
            config["llm"]["groq_api_key"] = cls.GROQ_API_KEY
            config["llm"]["openai_api_key"] = cls.OPENAI_API_KEY
        
        if "linkedin" in config:
            config["linkedin"]["username"] = cls.LINKEDIN_USERNAME
            config["linkedin"]["password"] = cls.LINKEDIN_PASSWORD
        
        return config
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        errors = []
        
        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            errors.append("Either GROQ_API_KEY or OPENAI_API_KEY must be set")
        
        if not cls.LINKEDIN_USERNAME or not cls.LINKEDIN_PASSWORD:
            errors.append("LINKEDIN_USERNAME and LINKEDIN_PASSWORD must be set for LinkedIn scraping")
        
        if errors:
            for error in errors:
                print(f"❌ Configuration Error: {error}")
            return False
        
        return True

config = Config()
