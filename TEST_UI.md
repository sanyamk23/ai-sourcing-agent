# 🧪 Testing the UI

## Quick Start

1. **Start the server**:
   ```bash
   ./start_ui.sh
   ```
   
   Or manually:
   ```bash
   python run_api.py
   ```

2. **Open your browser**:
   ```
   http://localhost:8000
   ```

3. **You should see**:
   - Beautiful header with logo and stats
   - Job creation form
   - Candidates table with existing data (6 candidates already in DB!)

## Test Scenarios

### Scenario 1: View Existing Candidates
✅ The table should already show 6 candidates from your database:
- Naina Tirthani (Data Engineer, Bangalore)
- Virendra Singh Rathore (Data Engineer, Bangalore)
- Manvitha Raju (Data Engineer, Bangalore)
- Vishal Singh (Senior Software Engineer)
- Karl Christian (Data Engineering)
- And more...

### Scenario 2: Search Functionality
1. Type "Data Engineer" in the search box
2. Table should filter to show only matching candidates
3. Try searching by location: "Bangalore"
4. Try searching by skills

### Scenario 3: Create a New Job
1. Fill out the form:
   ```
   Job Title: Senior Python Developer
   Location: San Francisco, CA
   Experience: 5
   Skills: Python, Django, PostgreSQL, AWS
   Description: Looking for an experienced Python developer...
   ```

2. Click "🚀 Start Sourcing Candidates"

3. **Watch the magic**:
   - Modal appears with loading spinner
   - Motivational HR facts rotate every 4 seconds
   - Progress bar animates
   - Facts include things like:
     * "💡 Companies with strong recruitment processes are 3.5x more likely to outperform..."
     * "🌟 Great hires don't just fill positions—they transform teams..."
     * And 13 more inspiring facts!

4. **After processing**:
   - Modal closes automatically
   - Success message appears
   - Candidates table refreshes with new candidates
   - Form resets for next job

### Scenario 4: View Candidate Details
1. Click the "View" button on any candidate
2. Alert shows full candidate details:
   - Name, Title, Email, Phone
   - Experience, Location, Education
   - All skills
   - Profile URL
   - Summary

### Scenario 5: Responsive Design
1. Resize your browser window
2. On mobile (<768px):
   - Form becomes single column
   - Stats stack vertically
   - Table scrolls horizontally

## API Endpoints Being Used

The UI interacts with these endpoints:

1. **POST /jobs** - Create new job
   ```javascript
   fetch('http://localhost:8000/jobs', {
     method: 'POST',
     body: JSON.stringify(jobData)
   })
   ```

2. **GET /jobs/{job_id}** - Poll job status
   ```javascript
   fetch('http://localhost:8000/jobs/abc-123')
   ```

3. **GET /candidates** - Load all candidates
   ```javascript
   fetch('http://localhost:8000/candidates')
   ```

## Expected Behavior

### ✅ What Should Work
- Form validation (required fields)
- Real-time search/filter
- Smooth animations
- Responsive layout
- Loading states
- Error handling

### 🎨 Visual Elements to Notice
- Gradient backgrounds
- Hover effects on buttons and rows
- Blue color scheme throughout
- Rounded corners
- Subtle shadows
- Skill tags with light blue background
- Smooth transitions

### ⏱️ Timing
- Facts rotate: Every 4 seconds
- Job polling: Every 5 seconds
- Max polling: 5 minutes (60 attempts)
- Progress bar: 3-second animation loop

## Troubleshooting

### UI doesn't load
- Check if server is running: `curl http://localhost:8000/health`
- Check browser console for errors (F12)
- Verify static files exist in `static/` folder

### No candidates showing
- Check database: `sqlite3 candidates.db "SELECT COUNT(*) FROM candidates;"`
- Check API: `curl http://localhost:8000/candidates`
- Check browser console for CORS errors

### Job creation fails
- Check API logs for errors
- Verify all required fields are filled
- Check GROQ_API_KEY in .env
- Check LinkedIn credentials if using LinkedIn scraping

### Facts not rotating
- Check browser console for JavaScript errors
- Verify app.js is loaded
- Check modal is visible (should have class "active")

## Browser Console Commands

Open browser console (F12) and try:

```javascript
// Check if candidates loaded
console.log(allCandidates);

// Manually trigger search
handleSearch({ target: { value: 'python' } });

// Check current fact
console.log(hrFacts[currentFactIndex]);

// Force refresh candidates
refreshCandidates();
```

## Success Indicators

✅ You'll know it's working when:
1. Page loads with beautiful blue/white design
2. Stats show "6" total candidates
3. Table displays 6 existing candidates
4. Search filters work in real-time
5. Form submission shows loading modal
6. Facts rotate automatically
7. Hover effects work smoothly

## Next Steps

After testing:
1. Customize colors in `static/styles.css`
2. Add more facts in `static/app.js`
3. Modify form fields as needed
4. Add more table columns
5. Implement candidate detail modal instead of alert
6. Add export to CSV functionality
7. Add job history view

Enjoy your beautiful new UI! 🎉
