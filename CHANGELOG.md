# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-27

### Added
- Initial production-ready release
- Multi-portal candidate scraping (LinkedIn, StackOverflow, Indeed, Glassdoor, GitHub)
- AI-powered candidate matching using embeddings
- LLM reasoning with Groq (free tier)
- Multi-factor candidate ranking
- REST API with FastAPI
- Database persistence with SQLAlchemy
- Docker support with docker-compose
- Comprehensive documentation
- Production deployment configurations
- Health checks and monitoring
- Logging with rotation
- Environment-based configuration
- Makefile for common tasks

### Fixed
- LinkedIn scraper updated for new HTML structure
- Selector changed from `.reusable-search__result-container` to `[data-chameleon-result-urn]`
- Added fallback selectors for robust data extraction
- Import path fixes for database module

### Security
- Environment variable management
- CORS configuration
- Secret key handling
- Rate limiting support

## [0.2.0] - 2024-11-26

### Added
- LinkedIn scraping with Selenium
- StackOverflow scraping
- Basic Indeed and Glassdoor scrapers
- AI matching with sentence transformers
- Groq LLM integration

### Changed
- Switched from OpenAI to Groq for cost savings
- Improved scraping reliability

## [0.1.0] - 2024-11-25

### Added
- Initial project structure
- Basic API endpoints
- Candidate and job models
- Configuration system
