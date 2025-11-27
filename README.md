# 🤖 AI Candidate Sourcing System

An intelligent, automated candidate sourcing system that uses AI to find, match, and rank candidates from multiple job portals.

## ✨ Features

- 🎨 **Beautiful Web UI**: Modern, responsive interface with light blue and white theme
- 🔍 **Multi-Portal Scraping**: Automatically scrapes candidates from LinkedIn, StackOverflow, Indeed, Glassdoor, and GitHub Jobs
- 🧠 **AI-Powered Matching**: Uses embeddings and LLM reasoning to match candidates to job requirements
- 📊 **Intelligent Ranking**: Multi-factor scoring based on skills, experience, and AI analysis
- 💡 **Motivational Facts**: Display inspiring HR facts while processing jobs
- 🚀 **REST API**: Easy-to-use API for job submission and candidate retrieval
- 💰 **FREE AI**: Uses Groq (free) for LLM operations - no OpenAI costs!
- 🐳 **Docker Ready**: Production-ready Docker configuration
- 📝 **Database Storage**: Persistent storage of jobs and candidates

## 🎯 Quick Start

### Prerequisites

- Python 3.12+
- LinkedIn account (for LinkedIn scraping)
- Groq API key (free from [groq.com](https://groq.com))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd linkedin
```

2. **Install dependencies**
```bash
make install
# or
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```env
GROQ_API_KEY=your_groq_api_key_here
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

4. **Run the API server**
```bash
make run
# or
python run_api.py
```

The API and Web UI will be available at `http://localhost:8000`

### 🎨 Using the Web UI

1. Open your browser and go to `http://localhost:8000`
2. Fill out the job creation form with:
   - Job title
   - Location
   - Required experience
   - Skills (comma-separated)
   - Job description
3. Click "🚀 Start Sourcing Candidates"
4. Enjoy motivational HR facts while AI finds candidates!
5. View all candidates in the table below with search functionality

See [UI_GUIDE.md](UI_GUIDE.md) for detailed UI documentation.

## 📖 API Documentation

### Submit a Job

```bash
POST /jobs
Content-Type: application/json

{
  "title": "Python Developer",
  "description": "Looking for experienced Python developer",
  "required_skills": ["Python", "Django", "FastAPI"],
  "experience_years": 3,
  "location": "San Francisco"
}
```

Response:
```json
{
  "id": "job-uuid",
  "status": "PENDING",
  "created_at": "2024-01-01T00:00:00"
}
```

### Get Job Status

```bash
GET /jobs/{job_id}
```

### Get Ranked Candidates

```bash
GET /jobs/{job_id}/candidates
```

Response:
```json
[
  {
    "candidate": {
      "id": "candidate-id",
      "name": "John Doe",
      "email": "john@example.com",
      "current_title": "Senior Python Developer",
      "skills": ["Python", "Django", "PostgreSQL"],
      "experience_years": 5,
      "location": "San Francisco",
      "profile_url": "https://linkedin.com/in/johndoe"
    },
    "match_score": 0.92,
    "rank_score": 95.5,
    "reasoning": "Strong match with 5 years Python experience..."
  }
]
```

### Interactive API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐳 Docker Deployment

### Build and Run

```bash
make docker-build
make docker-run
```

Or manually:
```bash
docker-compose up -d
```

### View Logs

```bash
make docker-logs
# or
docker-compose logs -f
```

### Stop

```bash
make docker-stop
# or
docker-compose down
```

## 🏗️ Project Structure

```
.
├── src/                      # Source code
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── agent.py             # Main orchestration
│   ├── api_server.py        # FastAPI server
│   ├── cache.py             # Caching layer
│   ├── config.py            # Configuration management
│   ├── database.py          # Database models
│   ├── enrichment.py        # Data enrichment
│   ├── llm_provider.py      # LLM integration
│   ├── logging_config.py    # Logging setup
│   ├── matcher.py           # AI matching
│   ├── models.py            # Data models
│   ├── proxy_manager.py     # Proxy management
│   ├── ranker.py            # Candidate ranking
│   ├── scrapers.py          # Portal scrapers
│   └── tasks.py             # Background tasks
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_*.py            # Test modules
├── scripts/                 # Utility scripts
│   ├── setup.sh             # Setup script
│   ├── verify_setup.py      # Verification
│   └── health_check.sh      # Health monitoring
├── docs/                    # Documentation
│   ├── API.md               # API documentation
│   └── DEPLOYMENT.md        # Deployment guide
├── data/                    # Database files (gitignored)
├── logs/                    # Log files (gitignored)
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Dev dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose
├── .dockerignore            # Docker ignore rules
├── Makefile                 # Build commands
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guide
└── README.md                # This file
```

## 🧪 Testing

Run all tests:
```bash
make test
# or
pytest tests/ -v
```

Run specific test:
```bash
pytest tests/test_linkedin_fixed.py -v
```

## 🔧 Development

### Install dev dependencies

```bash
make dev
```

### Code formatting

```bash
make format
```

### Linting

```bash
make lint
```

### Clean temporary files

```bash
make clean
```

## 📊 How It Works

1. **Job Submission**: User submits job description via API
2. **Parallel Scraping**: System scrapes multiple portals simultaneously
3. **AI Matching**: Uses embeddings to match candidates to requirements
4. **LLM Reasoning**: Groq AI generates detailed match reasoning
5. **Multi-Factor Ranking**: Combines multiple signals for final ranking
6. **Results**: Returns top 20 ranked candidates with explanations

## 🎯 Supported Portals

- ✅ **LinkedIn**: Real-time scraping with Selenium
- ✅ **StackOverflow**: Jobs and developer profiles
- ⚠️ **Indeed**: Basic scraping (limited by anti-bot)
- ⚠️ **Glassdoor**: Basic scraping (limited by anti-bot)
- ⚠️ **GitHub Jobs**: API-based (when available)

## 💡 Configuration

Edit `config.yaml` to customize:

- Scraping settings (max candidates, timeouts)
- LLM model selection
- Ranking weights
- Portal priorities

## 🌐 Persistent Browser Session (LinkedIn)

The LinkedIn scraper now uses a **persistent browser session** that stays open between searches:

### How it works:
- ✅ **First search**: Opens browser, logs into LinkedIn once
- ✅ **Subsequent searches**: Reuses the same browser, opens new tabs
- ✅ **No repeated logins**: Stay logged in across multiple job searches
- ✅ **Faster searches**: Skip login time on every search

### Benefits:
- 🚀 **Faster**: No need to login every time
- 🔐 **More reliable**: Avoid repeated CAPTCHA challenges
- 💻 **Better UX**: Browser stays open, you can monitor searches

### Manual browser control:

**To close the browser manually:**
```bash
python close_browser.py
```

**Browser behavior:**
- Browser window stays open after searches complete
- New searches open in new tabs automatically
- Browser closes when you stop the API server or run `close_browser.py`

### Tips:
- If you see a CAPTCHA, solve it in the browser window - it will be reused
- The browser window can be minimized while running
- Multiple job searches will open multiple tabs in the same window

## 🔒 Security

- Never commit `.env` file
- Use strong passwords
- Rotate API keys regularly
- Use environment variables in production
- Enable CORS restrictions in production

## 📈 Performance

- **Scraping**: 20-60 candidates in 30-60 seconds
- **AI Matching**: ~1 second per candidate
- **LLM Reasoning**: ~2-3 seconds per candidate (with Groq)
- **Total**: ~2-3 minutes for complete pipeline

## 🐛 Troubleshooting

### LinkedIn not working

- Check credentials in `.env`
- Solve CAPTCHA if prompted (browser stays open for this)
- LinkedIn may block automated access
- Browser session is reused - login once, use multiple times
- If browser gets stuck, run `python close_browser.py` and try again

### Groq API errors

- Check API key is valid
- Groq has rate limits (free tier)
- System auto-retries on rate limits

### Chrome/Selenium issues

- Install Chrome browser
- Update undetected-chromedriver
- Check Chrome version compatibility

## 📝 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For issues and questions:
- Open a GitHub issue
- Check existing documentation
- Review API docs at `/docs`

## 🎉 Acknowledgments

- Groq for free LLM API
- Sentence Transformers for embeddings
- FastAPI for the web framework
- Selenium for web scraping

---

**Built with ❤️ for recruiters and hiring teams**
