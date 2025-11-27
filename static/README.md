# AI Candidate Sourcing - UI Dashboard

A beautiful, modern web interface for the AI Candidate Sourcing system with light blue and white theme.

## Features

- 🎨 **Beautiful UI**: Clean, modern design with light blue and white color scheme
- 📝 **Job Creation Form**: Easy-to-use form to create new job postings
- 💡 **Motivational Facts**: Display inspiring HR facts while processing jobs
- 📊 **Candidates Table**: View all candidates with search and filter capabilities
- 🔄 **Real-time Updates**: Automatic polling for job status updates
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## Usage

1. Start the API server:
   ```bash
   python run_api.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. Create a new job by filling out the form
4. Watch motivational HR facts while the AI sources candidates
5. View all candidates in the table below

## Color Scheme

- Primary Blue: #4A90E2
- Light Blue: #E3F2FD
- Lighter Blue: #F0F8FF
- Dark Blue: #2C5F8D
- White: #FFFFFF

## API Endpoints Used

- `POST /jobs` - Create new job
- `GET /jobs/{job_id}` - Get job status
- `GET /candidates` - Get all candidates
