# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Submit Job

Submit a new job description for candidate sourcing.

**Endpoint:** `POST /jobs`

**Request Body:**
```json
{
  "title": "Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
  "experience_years": 3,
  "location": "San Francisco Bay Area"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "description": {
    "title": "Python Developer",
    "description": "We are looking for...",
    "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
    "experience_years": 3,
    "location": "San Francisco Bay Area"
  },
  "status": "PENDING",
  "created_at": "2024-01-01T12:00:00.000Z",
  "candidates": []
}
```

**Status Codes:**
- `200 OK`: Job created successfully
- `422 Unprocessable Entity`: Invalid request body

---

### 3. Get Job Status

Retrieve the status and details of a submitted job.

**Endpoint:** `GET /jobs/{job_id}`

**Path Parameters:**
- `job_id` (string, required): The UUID of the job

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "description": {
    "title": "Python Developer",
    "description": "We are looking for...",
    "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
    "experience_years": 3,
    "location": "San Francisco Bay Area"
  },
  "status": "COMPLETED",
  "created_at": "2024-01-01T12:00:00.000Z",
  "candidates": [...]
}
```

**Status Values:**
- `PENDING`: Job submitted, not yet processing
- `PROCESSING`: Currently sourcing candidates
- `COMPLETED`: Sourcing complete, candidates available
- `FAILED`: An error occurred during processing

**Status Codes:**
- `200 OK`: Job found
- `404 Not Found`: Job ID not found

---

### 4. Get Ranked Candidates

Retrieve the ranked list of candidates for a completed job.

**Endpoint:** `GET /jobs/{job_id}/candidates`

**Path Parameters:**
- `job_id` (string, required): The UUID of the job

**Response:**
```json
[
  {
    "candidate": {
      "id": "abc123",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-0123",
      "current_title": "Senior Python Developer",
      "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
      "experience_years": 5,
      "education": "BS Computer Science",
      "location": "San Francisco, CA",
      "profile_url": "https://linkedin.com/in/johndoe",
      "source_portal": "linkedin",
      "summary": "Experienced Python developer with 5 years..."
    },
    "match_score": 0.92,
    "rank_score": 95.5,
    "reasoning": "Strong candidate with 5 years of Python experience. Has all required skills including Django and FastAPI. Located in target area."
  },
  {
    "candidate": {
      "id": "def456",
      "name": "Jane Smith",
      "email": null,
      "phone": null,
      "current_title": "Python Developer",
      "skills": ["Python", "Flask", "PostgreSQL"],
      "experience_years": 3,
      "education": null,
      "location": "San Francisco, CA",
      "profile_url": "https://stackoverflow.com/users/12345",
      "source_portal": "stackoverflow",
      "summary": "Python developer with web development experience"
    },
    "match_score": 0.85,
    "rank_score": 87.3,
    "reasoning": "Good match with 3 years experience. Has Python and PostgreSQL skills. Missing Django/FastAPI but has Flask experience."
  }
]
```

**Status Codes:**
- `200 OK`: Candidates retrieved successfully
- `400 Bad Request`: Job not completed yet
- `404 Not Found`: Job ID not found

---

## Data Models

### JobDescription

```typescript
{
  title: string;              // Job title
  description: string;        // Detailed job description
  required_skills: string[];  // List of required skills
  experience_years: number;   // Minimum years of experience
  location?: string;          // Job location (optional)
}
```

### Candidate

```typescript
{
  id: string;                 // Unique candidate ID
  name: string;               // Candidate name
  email?: string;             // Email address (if available)
  phone?: string;             // Phone number (if available)
  current_title: string;      // Current job title
  skills: string[];           // List of skills
  experience_years: number;   // Years of experience
  education?: string;         // Education background
  location: string;           // Location
  profile_url: string;        // Profile URL
  source_portal: string;      // Source portal (linkedin, stackoverflow, etc.)
  summary: string;            // Brief summary
}
```

### RankedCandidate

```typescript
{
  candidate: Candidate;       // Candidate details
  match_score: number;        // AI match score (0-1)
  rank_score: number;         // Final rank score (0-100)
  reasoning: string;          // AI-generated reasoning
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400 Bad Request`: Invalid request or job not ready
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- Default: 60 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

When rate limited, you'll receive a `429 Too Many Requests` response.

---

## Examples

### cURL

```bash
# Submit a job
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "description": "Looking for Python developer",
    "required_skills": ["Python", "Django"],
    "experience_years": 3,
    "location": "San Francisco"
  }'

# Get job status
curl http://localhost:8000/jobs/{job_id}

# Get candidates
curl http://localhost:8000/jobs/{job_id}/candidates
```

### Python

```python
import requests

# Submit job
response = requests.post(
    "http://localhost:8000/jobs",
    json={
        "title": "Python Developer",
        "description": "Looking for Python developer",
        "required_skills": ["Python", "Django"],
        "experience_years": 3,
        "location": "San Francisco"
    }
)
job = response.json()
job_id = job["id"]

# Wait for completion (poll status)
import time
while True:
    response = requests.get(f"http://localhost:8000/jobs/{job_id}")
    job = response.json()
    if job["status"] == "COMPLETED":
        break
    time.sleep(5)

# Get candidates
response = requests.get(f"http://localhost:8000/jobs/{job_id}/candidates")
candidates = response.json()

for ranked in candidates[:5]:
    print(f"{ranked['candidate']['name']} - Score: {ranked['rank_score']}")
```

### JavaScript

```javascript
// Submit job
const response = await fetch('http://localhost:8000/jobs', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Python Developer',
    description: 'Looking for Python developer',
    required_skills: ['Python', 'Django'],
    experience_years: 3,
    location: 'San Francisco'
  })
});

const job = await response.json();
const jobId = job.id;

// Poll for completion
while (true) {
  const statusResponse = await fetch(`http://localhost:8000/jobs/${jobId}`);
  const jobStatus = await statusResponse.json();
  
  if (jobStatus.status === 'COMPLETED') break;
  await new Promise(resolve => setTimeout(resolve, 5000));
}

// Get candidates
const candidatesResponse = await fetch(`http://localhost:8000/jobs/${jobId}/candidates`);
const candidates = await candidatesResponse.json();

console.log(`Found ${candidates.length} candidates`);
```
