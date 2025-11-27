# 🚀 NoSQL Migration Guide

## Overview

This system now uses:
- **MongoDB** - NoSQL database for candidates and jobs
- **ChromaDB** - Vector database for semantic search and embeddings

## Why This Architecture?

### MongoDB (NoSQL)
- ✅ Flexible schema for varying candidate data
- ✅ Better performance for large datasets
- ✅ Easy to scale horizontally
- ✅ Native JSON support

### ChromaDB (Vector Database)
- ✅ Stores ALL scraped candidates (not just top 10-12)
- ✅ Semantic search using embeddings
- ✅ Find similar candidates automatically
- ✅ Better matching than keyword search

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install MongoDB

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Or use MongoDB Atlas (Cloud):**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create a free cluster
- Get connection string
- Add to `.env`: `MONGODB_URI=mongodb+srv://...`

### 3. Run Migration

```bash
python scripts/migrate_to_nosql.py
```

This will:
- ✅ Copy all candidates from SQLite to MongoDB
- ✅ Copy all jobs from SQLite to MongoDB
- ✅ Create vector embeddings for all candidates
- ✅ Verify the migration

## Usage

### Start the New API Server

```bash
# Use the new NoSQL server
python -m uvicorn src.api_server_nosql:app --reload --port 8000
```

Or update `run_api.py`:
```python
# Change from:
from src.api_server import app

# To:
from src.api_server_nosql import app
```

### How It Works Now

#### 1. **Scraping Phase**
When you create a job:
- System scrapes 50-100 candidates from multiple platforms
- **ALL scraped candidates** are stored in:
  - MongoDB `scraped_candidates` collection
  - ChromaDB `scraped_candidates` collection (with embeddings)

#### 2. **Filtering Phase**
- AI ranks and filters to top 10-12 candidates
- **Final candidates** are stored in:
  - MongoDB `candidates` collection
  - ChromaDB `candidates` collection (with embeddings)

#### 3. **Future Searches**
- When you create a new job, system first searches vector DB
- Finds similar candidates from ALL previously scraped data
- No need to re-scrape if similar candidates exist!

## API Changes

### New Endpoints

```bash
# Semantic search
GET /api/search/semantic?query=Python developer&n_results=10

# Health check (now shows DB stats)
GET /health
```

### Updated Endpoints

All existing endpoints work the same:
- `POST /jobs` - Create job
- `GET /api/jobs/all` - Get all jobs
- `GET /api/candidates` - Get all candidates
- `POST /api/candidate/{id}/scrape-linkedin` - Scrape profile

## Database Structure

### MongoDB Collections

#### `candidates` (Final selected candidates)
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "current_title": "Senior Python Developer",
  "skills": ["Python", "Django", "AWS"],
  "experience_years": 5,
  "location": "San Francisco",
  "profile_url": "https://linkedin.com/in/johndoe",
  "source_portal": "LinkedIn",
  "summary": "...",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### `scraped_candidates` (All scraped data)
```json
{
  "profile_url": "https://linkedin.com/in/janedoe",
  "name": "Jane Doe",
  "current_title": "Data Engineer",
  "skills": ["Python", "Spark", "SQL"],
  "source_portal": "LinkedIn",
  "scraped_at": "2024-01-01T00:00:00",
  ...
}
```

#### `jobs`
```json
{
  "id": "uuid",
  "title": "Senior Python Developer",
  "description": "...",
  "required_skills": ["Python", "Django"],
  "experience_years": 5,
  "location": "San Francisco",
  "status": "completed",
  "candidates": [...],
  "created_at": "2024-01-01T00:00:00"
}
```

### ChromaDB Collections

#### `candidates` - Vector embeddings of final candidates
#### `scraped_candidates` - Vector embeddings of ALL scraped candidates

## Benefits

### 1. **No Data Loss**
- Previously: Scraped 100 candidates, kept only 10
- Now: All 100 stored in vector DB for future use

### 2. **Faster Searches**
- Previously: Re-scrape for every job
- Now: Search existing pool first, scrape only if needed

### 3. **Better Matching**
- Previously: Keyword matching
- Now: Semantic similarity using AI embeddings

### 4. **Scalability**
- MongoDB can handle millions of candidates
- ChromaDB optimized for vector search

## Example: Semantic Search

```python
# Search for similar candidates
results = vector_db.semantic_search(
    query="experienced Python developer with AWS and Docker",
    n_results=20
)

# Results are ranked by semantic similarity
for result in results:
    print(f"{result['metadata']['name']} - {result['metadata']['title']}")
    print(f"Similarity score: {result['distance']}")
```

## Monitoring

### Check Database Status

```bash
# MongoDB
mongo
> use candidate_sourcing
> db.candidates.count()
> db.scraped_candidates.count()

# ChromaDB
python
>>> from src.vector_database import vector_db
>>> vector_db.get_collection_count(is_final=True)
>>> vector_db.get_collection_count(is_final=False)
```

## Backup

### MongoDB Backup
```bash
mongodump --db candidate_sourcing --out ./backup
```

### MongoDB Restore
```bash
mongorestore --db candidate_sourcing ./backup/candidate_sourcing
```

### ChromaDB Backup
ChromaDB data is stored in `./chroma_db/` directory. Just copy this folder.

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
brew services list  # macOS
sudo systemctl status mongodb  # Linux

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongodb  # Linux
```

### ChromaDB Error
```bash
# Clear and rebuild
rm -rf ./chroma_db
python scripts/migrate_to_nosql.py
```

## Performance

- **MongoDB**: Handles 1M+ candidates easily
- **ChromaDB**: Fast vector search (<100ms for 10K candidates)
- **Embeddings**: Generated once, reused forever

## Next Steps

1. ✅ Run migration script
2. ✅ Test with existing data
3. ✅ Create new jobs (will use vector search)
4. ✅ Monitor performance
5. ✅ Scale as needed

---

**Questions?** Check the logs or API documentation at `/docs`
