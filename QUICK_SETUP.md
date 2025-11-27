# 🚀 Quick Setup Guide

## Fix urllib3 Warning (Optional)

```bash
pip install --upgrade urllib3==2.5.0
```

## Install MongoDB

### Option 1: MongoDB Community (Local)

```bash
# Add MongoDB tap
brew tap mongodb/brew

# Install MongoDB
brew install mongodb-community@8.0

# Start MongoDB
brew services start mongodb-community@8.0

# Verify it's running
brew services list | grep mongodb
```

### Option 2: MongoDB Atlas (Cloud - Recommended for Easy Setup)

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free
3. Create a free cluster (M0)
4. Get connection string
5. Add to `.env`:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/candidate_sourcing
   ```

### Option 3: Use Docker (Easiest)

```bash
# Run MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Check if running
docker ps | grep mongodb
```

## Run Migration

```bash
# Migrate existing data
python scripts/migrate_to_nosql.py
```

## Start Server

```bash
# Use new NoSQL server
python -m uvicorn src.api_server_nosql:app --reload --port 8000
```

## Verify Everything Works

```bash
# Check health
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "database": "MongoDB + ChromaDB",
#   "candidates_count": 6,
#   "jobs_count": 2,
#   "vector_db_count": 6
# }
```

## If MongoDB Installation Fails

Just use the Docker option - it's the easiest:

```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop

# Then run:
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Test the System

1. Open http://localhost:8000
2. Create a new job
3. System will:
   - Scrape candidates
   - Store ALL in MongoDB + ChromaDB
   - Show top 10-12 in UI
   - Keep rest for future searches

## Troubleshooting

### MongoDB won't start
```bash
# Check if port 27017 is in use
lsof -i :27017

# Kill any process using it
kill -9 <PID>

# Try starting again
brew services restart mongodb-community@8.0
```

### ChromaDB errors
```bash
# Clear and rebuild
rm -rf ./chroma_db
python scripts/migrate_to_nosql.py
```

### Migration fails
```bash
# Check if MongoDB is running
mongosh

# If connected, you're good!
# If not, start MongoDB first
```

## Next Steps

1. ✅ MongoDB running
2. ✅ Migration complete
3. ✅ Server started
4. ✅ Create a test job
5. ✅ See all scraped candidates stored

---

**Need help?** Check logs or visit http://localhost:8000/docs
