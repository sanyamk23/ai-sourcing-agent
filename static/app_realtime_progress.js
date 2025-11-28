// Real-time Progress Update Functions
// Add these to app.js to replace the fake animation

// Update Workflow Progress Based on Real Backend Status
function updateWorkflowProgress(progress) {
    const stepMap = {
        'extracting': 1,
        'searching': 2,
        'building': 3,
        'matching': 4,
        'completed': 4
    };
    
    const currentStep = stepMap[progress.step_name] || 1;
    
    // Update progress bar
    document.getElementById('overallProgress').style.width = `${progress.progress}%`;
    document.getElementById('progressText').textContent = progress.message;
    
    // Update step statuses
    for (let i = 1; i <= 4; i++) {
        const stepElement = document.getElementById(`step${i}`);
        const statusText = stepElement.querySelector('.status-text');
        
        if (i < currentStep) {
            // Completed steps
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
            statusText.textContent = 'Done';
            
            // Activate connector
            if (i < 4) {
                document.getElementById(`connector${i}`).classList.add('active');
            }
        } else if (i === currentStep) {
            // Current step
            stepElement.classList.add('active');
            stepElement.classList.remove('completed');
            statusText.textContent = 'Processing...';
        } else {
            // Future steps
            stepElement.classList.remove('active', 'completed');
            statusText.textContent = 'Waiting...';
        }
    }
    
    // Show candidate count if available
    if (progress.candidates_found > 0 && currentStep >= 3) {
        const step3 = document.getElementById('step3');
        const step3Text = step3.querySelector('.step-content p');
        step3Text.textContent = `Found ${progress.candidates_found} candidates`;
    }
}

// Poll Job Status with Real-Time Progress
async function pollJobStatusRealtime(jobId) {
    const maxAttempts = 60;
    let attempts = 0;
    let scrapingComplete = false;
    let previousCandidateCount = 0;

    const poll = async () => {
        try {
            // Fetch both job status and progress
            const [jobResponse, progressResponse] = await Promise.all([
                fetch(`${API_BASE_URL}/jobs/${jobId}`),
                fetch(`${API_BASE_URL}/jobs/${jobId}/progress`)
            ]);
            
            const job = await jobResponse.json();
            const progress = await progressResponse.json();
            
            // Update workflow animation based on real progress
            updateWorkflowProgress(progress);

            // Check if scraping is done (candidates found but still processing)
            if (!scrapingComplete && job.candidates && job.candidates.length > 0 && job.status === 'processing') {
                const currentCount = job.candidates.length;
                
                // Only trigger once when candidates first appear
                if (currentCount > previousCandidateCount) {
                    scrapingComplete = true;
                    previousCandidateCount = currentCount;
                    
                    // Wait a moment, then show matching modal with smooth transition
                    setTimeout(() => {
                        hideFactsModal();
                        setTimeout(() => showMatchingModal(currentCount), 200);
                    }, 800);
                }
            }

            if (job.status === 'completed') {
                // Close matching modal if open
                hideMatchingModal();
                
                // Reset form and load jobs
                document.getElementById('jobForm').reset();
                await loadJobs(true); // Auto-expand latest job
                
                // Scroll to results
                setTimeout(() => {
                    document.querySelector('.jobs-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
                
                // Show success notification
                showNotification(`🎉 Matched ${job.candidates?.length || 0} top candidates!`, 'success');
                return;
            } else if (job.status === 'failed') {
                hideFactsModal();
                hideMatchingModal();
                showNotification('❌ Job processing failed. Please try again.', 'error');
                return;
            }

            attempts++;
            if (attempts < maxAttempts) {
                // Poll very frequently (every 500ms) for instant updates
                setTimeout(poll, 500);
            } else {
                hideFactsModal();
                hideMatchingModal();
                showNotification('⏱️ Job is taking longer than expected. Check back later.', 'warning');
            }
        } catch (error) {
            console.error('Polling error:', error);
            hideFactsModal();
            hideMatchingModal();
            showNotification('❌ Error checking job status', 'error');
        }
    };

    poll();
}
