// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Platform logos mapping
const platformLogos = {
    'LinkedIn': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg',
    'Indeed': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/indeed.svg',
    'Stack Overflow': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/stackoverflow.svg',
    'StackOverflow': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/stackoverflow.svg',
    'Glassdoor': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/glassdoor.svg',
    'GitHub': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg',
    'GitHub Jobs': 'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg'
};

// Motivational HR Facts
const hrFacts = [
    "💡 Did you know? Companies with strong recruitment processes are 3.5x more likely to outperform their competitors.",
    "🌟 Great hires don't just fill positions—they transform teams and drive innovation.",
    "📊 70% of the global workforce is made up of passive talent. AI helps you reach them!",
    "🎯 Quality of hire is the #1 metric for measuring recruitment success.",
    "💼 The best candidates are off the market in just 10 days. Speed matters!",
    "🚀 Companies that invest in recruitment technology see 40% faster time-to-hire.",
    "🤝 Employee referrals have the highest retention rate at 45% after two years.",
    "✨ A positive candidate experience increases the likelihood of acceptance by 38%.",
    "📈 Data-driven recruitment decisions lead to 50% better quality hires.",
    "🎓 Diverse teams are 35% more likely to outperform their peers.",
    "💪 The right hire can increase team productivity by up to 40%.",
    "🌍 Remote work has expanded your talent pool by 10x. Think globally!",
    "⚡ AI-powered sourcing reduces time-to-hire by an average of 50%.",
    "🎨 Cultural fit is important, but skills can be taught. Focus on potential!",
    "🔍 Passive candidates make up 73% of the workforce—they're worth the effort!"
];

let currentFactIndex = 0;
let factInterval;
let allJobs = [];
let expandedJobId = null;
let currentPages = {}; // Track current page for each job
const ITEMS_PER_PAGE = 5;

// Scroll to dashboard
function scrollToDashboard() {
    document.getElementById('dashboardSection').scrollIntoView({ behavior: 'smooth' });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    setupEventListeners();
    createParticles();
});

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('jobForm').addEventListener('submit', handleJobSubmit);
}

// Handle Job Form Submission
async function handleJobSubmit(e) {
    e.preventDefault();
    
    const jobData = {
        title: document.getElementById('jobTitle').value,
        description: document.getElementById('description').value,
        required_skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
        experience_years: parseInt(document.getElementById('experience').value),
        location: document.getElementById('location').value
    };

    try {
        showFactsModal();
        
        const response = await fetch(`${API_BASE_URL}/jobs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jobData)
        });

        if (!response.ok) {
            throw new Error('Failed to create job');
        }

        const job = await response.json();
        console.log('Job created:', job);

        await pollJobStatus(job.id);
        
    } catch (error) {
        console.error('Error:', error);
        hideFactsModal();
        alert('Error creating job. Please check the console and try again.');
    }
}

// Show Workflow Animation Modal
function showFactsModal() {
    const modal = document.getElementById('factsModal');
    modal.classList.add('active');
    
    // Reset all steps
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        step.classList.remove('active', 'completed');
        step.querySelector('.status-text').textContent = 'Waiting...';
        
        if (i < 4) {
            document.getElementById(`connector${i}`).classList.remove('active');
        }
    }
    
    // Reset progress
    document.getElementById('overallProgress').style.width = '0%';
    document.getElementById('progressText').textContent = 'Initializing AI agents...';
    
    // Start workflow animation
    animateWorkflow();
}

// Animate Workflow Steps (FASTER)
function animateWorkflow() {
    const steps = [
        { id: 1, name: 'Phase 1: Scraping', duration: 30000, progress: 40, text: 'Scraping Naukri, LinkedIn, StackOverflow, GitHub...' },
        { id: 2, name: 'Phase 2: Vector Search', duration: 3000, progress: 60, text: 'Searching Vector DB for relevant candidates...' },
        { id: 3, name: 'Phase 3: Hard Matching', duration: 5000, progress: 80, text: 'Matching skills and experience requirements...' },
        { id: 4, name: 'Phase 4: Balancing', duration: 2000, progress: 100, text: 'Balancing results across sources...' }
    ];
    
    let currentStep = 0;
    
    function activateStep(stepIndex) {
        if (stepIndex >= steps.length) return;
        
        const step = steps[stepIndex];
        const stepElement = document.getElementById(`step${step.id}`);
        const progressBar = document.getElementById('overallProgress');
        const progressText = document.getElementById('progressText');
        
        // Activate current step
        stepElement.classList.add('active');
        stepElement.querySelector('.status-text').textContent = 'Processing...';
        
        // Update progress
        progressBar.style.width = `${step.progress}%`;
        progressText.textContent = step.text;
        
        // Complete step after duration
        setTimeout(() => {
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
            stepElement.querySelector('.status-text').textContent = 'Done';
            
            // Activate connector
            if (step.id < 4) {
                document.getElementById(`connector${step.id}`).classList.add('active');
            }
            
            // Move to next step
            activateStep(stepIndex + 1);
        }, step.duration);
    }
    
    // Start with first step
    activateStep(0);
}

// Hide Facts Modal
function hideFactsModal() {
    const modal = document.getElementById('factsModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none'; // Force hide
        setTimeout(() => modal.style.display = '', 100); // Reset after animation
    }
}

// Poll Job Status
async function pollJobStatus(jobId) {
    const maxAttempts = 90;  // Increased to 90 (3 minutes total: 90 * 2s = 180s)
    let attempts = 0;
    let scrapingComplete = false;
    let previousCandidateCount = 0;

    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
            const job = await response.json();

            // Check if scraping is done (candidates found but still processing)
            if (!scrapingComplete && job.candidates && job.candidates.length > 0 && job.status === 'processing') {
                const currentCount = job.candidates.length;
                
                // Only trigger once when candidates first appear
                if (currentCount > previousCandidateCount) {
                    scrapingComplete = true;
                    previousCandidateCount = currentCount;
                    
                    // Show candidates immediately
                    document.getElementById('overallProgress').style.width = '75%';
                    document.getElementById('progressText').textContent = `✅ Found ${currentCount} candidates! Now matching...`;
                    
                    // Wait a moment, then show matching modal with smooth transition
                    setTimeout(() => {
                        hideFactsModal();
                        setTimeout(() => showMatchingModal(currentCount), 200);
                    }, 800);
                }
            }

            if (job.status === 'completed') {
                // Close ALL modals
                hideFactsModal();
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
                // Poll every 2 seconds
                setTimeout(poll, 2000);
            } else {
                hideFactsModal();
                hideMatchingModal();
                showNotification('⏱️ Job is still processing. Refresh the page in a minute to see results.', 'warning');
                // Still load jobs to show the in-progress job
                await loadJobs();
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

// Show Matching Modal (Phase 2)
function showMatchingModal(candidateCount) {
    const modal = document.getElementById('matchingModal');
    modal.classList.add('active');
    
    // Set candidate count
    document.getElementById('candidateCount').textContent = candidateCount;
    
    // Animate the matching process
    animateMatching(candidateCount);
}

// Animate Matching Process (FASTER & MORE INTERACTIVE)
function animateMatching(candidateCount) {
    const messages = [
        'Extracting keywords from job description...',
        'Analyzing candidate skills and experience...',
        'Calculating semantic similarity scores...',
        'Ranking candidates by match quality...',
        'Generating AI insights for top matches...'
    ];
    
    let messageIndex = 0;
    let progress = 0;
    
    // Update message every 1 second (faster)
    const messageInterval = setInterval(() => {
        if (messageIndex < messages.length) {
            document.getElementById('matchingText').textContent = messages[messageIndex];
            messageIndex++;
        }
    }, 1000);
    
    // Animate stats (faster)
    animateCounter('keywordsExtracted', 0, Math.min(15, candidateCount), 1500);
    animateCounter('candidatesMatched', 0, candidateCount, 2000);
    animateCounter('topCandidates', 0, Math.min(20, candidateCount), 2500);
    
    // Animate progress bar (faster, smoother)
    const progressInterval = setInterval(() => {
        progress += 3;  // Faster increment
        document.getElementById('matchingProgress').style.width = `${Math.min(progress, 100)}%`;
        
        if (progress >= 100) {
            clearInterval(progressInterval);
            clearInterval(messageInterval);
        }
    }, 80);  // Smoother animation
}

// Animate Counter
function animateCounter(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    const range = end - start;
    const increment = range / (duration / 50);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            element.textContent = Math.round(end);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 50);
}

// Hide Matching Modal
function hideMatchingModal() {
    const modal = document.getElementById('matchingModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none'; // Force hide
        setTimeout(() => modal.style.display = '', 100); // Reset after animation
    }
}

// Show Notification (Toast)
function showNotification(message, type = 'success') {
    // Remove existing notification
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Hide after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Load Jobs from Database
async function loadJobs(autoExpandLatest = false) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/jobs/all`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch jobs');
        }

        allJobs = await response.json();
        
        // Auto-expand the latest job if requested
        if (autoExpandLatest && allJobs.length > 0) {
            expandedJobId = allJobs[0].id;
        }
        
        displayJobs(allJobs);
        updateStats();
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobsList').innerHTML = `
            <p class="no-data">Unable to load jobs. Make sure the API is running.</p>
        `;
    }
}

// Display Jobs with their Candidates (Accordion + Pagination)
function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (!jobs || jobs.length === 0) {
        jobsList.innerHTML = `<p class="no-data">No jobs yet. Create your first job above!</p>`;
        return;
    }

    // Set first job as expanded by default if none is expanded
    if (expandedJobId === null && jobs.length > 0) {
        expandedJobId = jobs[0].id;
    }

    jobsList.innerHTML = jobs.map((job, index) => {
        const candidates = job.candidates || [];
        const skills = Array.isArray(job.required_skills) ? job.required_skills : 
                      (job.required_skills ? JSON.parse(job.required_skills) : []);
        const isExpanded = expandedJobId === job.id;
        
        // Initialize page for this job if not exists
        if (!currentPages[job.id]) {
            currentPages[job.id] = 1;
        }
        
        const currentPage = currentPages[job.id];
        const totalPages = Math.ceil(candidates.length / ITEMS_PER_PAGE);
        const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
        const endIdx = startIdx + ITEMS_PER_PAGE;
        const paginatedCandidates = candidates.slice(startIdx, endIdx);
        
        return `
            <div class="job-card ${isExpanded ? 'expanded' : ''}" id="job-${job.id}">
                <div class="job-header" onclick="toggleJob('${job.id}')">
                    <div class="job-header-left">
                        <div class="job-info">
                            <h3>${job.title || 'Untitled Job'}</h3>
                            <div class="job-meta">
                                <span>📍 ${job.location || 'N/A'}</span>
                                <span>💼 ${job.experience_years || 0}+ years</span>
                                <span>👥 ${candidates.length} candidates</span>
                                <span>📅 ${new Date(job.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>
                    <div class="job-header-actions">
                        <button class="btn-rerun" onclick="event.stopPropagation(); rerunJobSearch('${job.id}')" title="Re-run this search">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M23 20V14H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M23 14L18.36 18.36A9 9 0 0 1 3.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            <span>Re-run Search</span>
                        </button>
                        <div class="job-toggle">
                            <span>${isExpanded ? 'Hide' : 'Show'} Details</span>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <div class="job-content">
                    <div class="job-content-inner">
                        ${skills.length > 0 ? `
                            <div class="job-skills">
                                ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                            </div>
                        ` : ''}
                        
                        ${candidates.length > 0 ? `
                            <div class="selection-note">
                                <div class="note-icon">ℹ️</div>
                                <div class="note-content">
                                    <strong>Selection Process:</strong> Showing all ${candidates.length} candidates from our vetted pool who passed the criteria 
                                    (min 10% skill match + 10% experience match). Results are balanced across Naukri, LinkedIn, StackOverflow, and GitHub. 
                                    <span class="top-3-badge">🏆 Top 3</span> matches are highlighted below.
                                </div>
                            </div>
                            <div class="candidates-table">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Rank</th>
                                            <th>Name</th>
                                            <th>Title</th>
                                            <th>Skills</th>
                                            <th>Experience</th>
                                            <th>Location</th>
                                            <th>Source</th>
                                            <th>Score</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${paginatedCandidates.map((candidate, idx) => {
                                            const cand = candidate.candidate || candidate;
                                            const candSkills = cand.skills ? 
                                                (Array.isArray(cand.skills) ? cand.skills : JSON.parse(cand.skills)) : [];
                                            const platform = cand.source_portal || 'Unknown';
                                            
                                            // Get match details
                                            const matchedSkills = candidate.match_breakdown?.matched_skills || [];
                                            const matchedSkillsLower = matchedSkills.map(s => s.toLowerCase());
                                            const isTop3 = candidate.match_breakdown?.is_top_3 || false;
                                            const rank = candidate.match_breakdown?.rank || (startIdx + idx + 1);
                                            const score = candidate.match_score || 0;
                                            
                                            return `
                                                <tr class="${isTop3 ? 'top-3-row' : ''}">
                                                    <td><strong>${isTop3 ? '🏆 ' : ''}#${rank}</strong></td>
                                                    <td><strong>${cand.name || 'N/A'}</strong></td>
                                                    <td>${cand.current_title || 'N/A'}</td>
                                                    <td>
                                                        ${candSkills.slice(0, 5).map(skill => {
                                                            const isMatched = matchedSkillsLower.includes(skill.toLowerCase());
                                                            return `<span class="skill-tag ${isMatched ? 'skill-matched' : ''}" title="${isMatched ? 'Matches job requirement' : ''}">${skill}${isMatched ? ' ✓' : ''}</span>`;
                                                        }).join('')}
                                                        ${candSkills.length > 5 ? `<span class="skill-tag">+${candSkills.length - 5}</span>` : ''}
                                                    </td>
                                                    <td>${cand.experience_years || 0} years</td>
                                                    <td>${cand.location || 'N/A'}</td>
                                                    <td>
                                                        <span class="platform-badge" style="background: ${getPlatformColor(platform)}; color: white; border: none;">
                                                            ${getPlatformIcon(platform)}
                                                            ${platform}
                                                        </span>
                                                    </td>
                                                    <td><strong>${(score * 100).toFixed(0)}%</strong></td>
                                                    <td>
                                                        <button class="btn-view" onclick='viewCandidate(${JSON.stringify(cand).replace(/'/g, "&apos;")})'>View</button>
                                                    </td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                                
                                ${totalPages > 1 ? `
                                    <div class="pagination">
                                        <button onclick="changePage('${job.id}', ${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                                            ← Previous
                                        </button>
                                        <span class="page-info">Page ${currentPage} of ${totalPages}</span>
                                        <button onclick="changePage('${job.id}', ${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                                            Next →
                                        </button>
                                    </div>
                                ` : ''}
                            </div>
                        ` : '<p class="no-data">No candidates found for this job yet.</p>'}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Toggle job accordion
function toggleJob(jobId) {
    if (expandedJobId === jobId) {
        expandedJobId = null;
    } else {
        expandedJobId = jobId;
    }
    displayJobs(allJobs);
}

// Change page for a job's candidates
function changePage(jobId, newPage) {
    currentPages[jobId] = newPage;
    displayJobs(allJobs);
}

// Create animated particles for landing page
function createParticles() {
    const landingSection = document.querySelector('.landing-section');
    if (!landingSection) return;
    
    // Create 30 particles for more visible effect
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Vary particle sizes
        const size = Math.random() * 8 + 3;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.bottom = '-20px';
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 15}s`;
        
        landingSection.appendChild(particle);
    }
    
    // Add some larger floating elements
    for (let i = 0; i < 5; i++) {
        const floater = document.createElement('div');
        floater.style.position = 'absolute';
        floater.style.width = `${50 + Math.random() * 100}px`;
        floater.style.height = `${50 + Math.random() * 100}px`;
        floater.style.borderRadius = '50%';
        floater.style.background = `radial-gradient(circle, rgba(255, 255, 255, ${0.1 + Math.random() * 0.1}) 0%, transparent 70%)`;
        floater.style.left = `${Math.random() * 100}%`;
        floater.style.top = `${Math.random() * 100}%`;
        floater.style.animation = `floatOrb ${20 + Math.random() * 20}s ease-in-out infinite`;
        floater.style.animationDelay = `${Math.random() * 10}s`;
        floater.style.pointerEvents = 'none';
        floater.style.zIndex = '0';
        
        landingSection.appendChild(floater);
    }
}

// View Candidate Details with Experience
async function viewCandidate(candidate) {
    // Show loading modal
    showCandidateModal(candidate, true);
    
    try {
        // Fetch detailed profile
        const response = await fetch(`${API_BASE_URL}/api/candidate/${candidate.id}/profile`);
        if (response.ok) {
            const profile = await response.json();
            showCandidateModal(profile, false);
        } else {
            showCandidateModal(candidate, false);
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
        showCandidateModal(candidate, false);
    }
}

// Show candidate modal with experience
function showCandidateModal(candidate, isLoading) {
    const skills = candidate.skills ? 
        (Array.isArray(candidate.skills) ? candidate.skills : JSON.parse(candidate.skills)) 
        : [];
    
    const matchScore = candidate.match_score ? 
        `<div class="match-score">Match Score: ${(candidate.match_score * 100).toFixed(0)}%</div>` : '';
    
    const reasoning = candidate.reasoning ? 
        `<div class="reasoning"><strong>AI Reasoning:</strong><p>${candidate.reasoning}</p></div>` : '';
    
    const experience = candidate.experience || [];
    
    const modalHTML = `
        <div class="candidate-modal-overlay" onclick="closeCandidateModal()">
            <div class="candidate-modal" onclick="event.stopPropagation()">
                <button class="modal-close" onclick="closeCandidateModal()">×</button>
                
                ${isLoading ? `
                    <div class="modal-loading">
                        <div class="loader"></div>
                        <p>Loading profile details...</p>
                    </div>
                ` : `
                    <div class="modal-header">
                        <h2>${candidate.name || 'N/A'}</h2>
                        <p class="modal-title">${candidate.current_title || 'N/A'}</p>
                        <div class="modal-meta">
                            <span>📍 ${candidate.location || 'N/A'}</span>
                            <span>💼 ${candidate.experience_years || 0} years</span>
                            <span style="background: ${getPlatformColor(candidate.source_portal)}; color: white; padding: 4px 12px; border-radius: 6px;">
                                ${getPlatformIcon(candidate.source_portal)} ${candidate.source_portal || 'N/A'}
                            </span>
                        </div>
                    </div>
                    
                    ${matchScore}
                    
                    <div class="modal-section">
                        <h3>Contact Information</h3>
                        <div class="contact-grid">
                            <div><strong>Email:</strong> ${candidate.email || 'N/A'}</div>
                            <div><strong>Phone:</strong> ${candidate.phone || 'N/A'}</div>
                            <div><strong>Education:</strong> ${candidate.education || 'N/A'}</div>
                            ${candidate.profile_url ? `<div><strong>Profile:</strong> <a href="${candidate.profile_url}" target="_blank">View LinkedIn →</a></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="modal-section">
                        <h3>Skills</h3>
                        <div class="skills-list">
                            ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                        </div>
                    </div>
                    
                    ${experience.length > 0 ? `
                        <div class="modal-section">
                            <h3>Work Experience</h3>
                            <div class="experience-list">
                                ${experience.map(exp => `
                                    <div class="experience-item">
                                        <div class="exp-header">
                                            <strong>${exp.title || 'Position'}</strong>
                                            <span class="exp-duration">${exp.duration || ''}</span>
                                        </div>
                                        <div class="exp-company">${exp.company || ''}</div>
                                        ${exp.description ? `<div class="exp-description">${exp.description}</div>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${candidate.summary ? `
                        <div class="modal-section">
                            <h3>Summary</h3>
                            <p class="summary-text">${candidate.summary}</p>
                        </div>
                    ` : ''}
                    
                    ${reasoning}
                `}
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.querySelector('.candidate-modal-overlay');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.body.style.overflow = 'hidden';
}

// Close candidate modal
function closeCandidateModal() {
    const modal = document.querySelector('.candidate-modal-overlay');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

// Update Statistics
function updateStats() {
    const totalCandidates = allJobs.reduce((sum, job) => {
        return sum + (job.candidates ? job.candidates.length : 0);
    }, 0);
    
    document.getElementById('totalCandidates').textContent = totalCandidates;
    document.getElementById('totalJobs').textContent = allJobs.length;
}

// Get platform color
function getPlatformColor(platform) {
    const colors = {
        'LinkedIn': '#0A66C2',
        'Indeed': '#2164F3',
        'Stack Overflow': '#F48024',
        'StackOverflow': '#F48024',
        'Glassdoor': '#0CAA41',
        'GitHub': '#181717',
        'GitHub Jobs': '#181717'
    };
    return colors[platform] || '#0555C8';
}

// Get platform icon (emoji)
function getPlatformIcon(platform) {
    const icons = {
        'LinkedIn': '💼',
        'Indeed': '🔍',
        'Stack Overflow': '📚',
        'StackOverflow': '📚',
        'Glassdoor': '🏢',
        'GitHub': '💻',
        'GitHub Jobs': '💻'
    };
    return icons[platform] || '🌐';
}

// Refresh Jobs
function refreshJobs() {
    loadJobs();
}

// Re-run Job Search
async function rerunJobSearch(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (!job) {
        alert('Job not found');
        return;
    }
    
    const confirmed = confirm(`Re-run search for "${job.title}"?\n\nThis will search for new candidates using the same job criteria.`);
    if (!confirmed) return;
    
    const jobData = {
        title: job.title,
        description: job.description,
        required_skills: Array.isArray(job.required_skills) ? job.required_skills : JSON.parse(job.required_skills),
        experience_years: job.experience_years,
        location: job.location
    };
    
    try {
        showFactsModal();
        
        const response = await fetch(`${API_BASE_URL}/jobs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jobData)
        });

        if (!response.ok) {
            throw new Error('Failed to re-run job search');
        }

        const newJob = await response.json();
        console.log('Job re-run started:', newJob);

        await pollJobStatus(newJob.id);
        
    } catch (error) {
        console.error('Error:', error);
        hideFactsModal();
        alert('Error re-running job search. Please try again.');
    }
}
