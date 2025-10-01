document.addEventListener('DOMContentLoaded', () => {

    // --- Select all the necessary HTML elements ---
    const welcomeSection = document.getElementById('welcome-section');
    const choiceSection = document.getElementById('choice-section');
    const appSection = document.getElementById('app-section');

    const getStartedBtn = document.getElementById('get-started-btn');
    const choiceRecommenderBtn = document.getElementById('choice-recommender-btn');
    const choiceSkillGapBtn = document.getElementById('choice-skill-gap-btn');
    const backBtn = document.getElementById('back-btn');

    const searchForm = document.getElementById('search-form');
    const appHeader = document.getElementById('app-header');
    const jobTitleGroup = document.getElementById('job-title-group');
    const jobTitleInput = document.getElementById('job-title-input');
    const skillsInput = document.getElementById('skills-input');
    const resumeInput = document.getElementById('resume-input');
    const uploadStatus = document.getElementById('upload-status');
    
    const resultsList = document.getElementById('results-list');
    const loader = document.getElementById('loader');

    let currentMode = ''; 
    const API_URL = 'http://localhost:8000';

    // Configure pdf.js worker
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js`;

    // --- Page Navigation ---
    function showPage(pageId) {
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById(pageId).classList.add('active');
    }

    // --- Event Listeners ---
    getStartedBtn.addEventListener('click', () => showPage('choice-section'));
    backBtn.addEventListener('click', () => {
        jobTitleInput.value = '';
        skillsInput.value = '';
        resumeInput.value = '';
        uploadStatus.textContent = '';
        resultsList.innerHTML = '';
        showPage('choice-section');
    });

    choiceRecommenderBtn.addEventListener('click', () => {
        currentMode = 'recommender';
        appHeader.textContent = 'Job Recommender';
        jobTitleGroup.style.display = 'none';
        jobTitleInput.required = false;
        skillsInput.required = true;
        showPage('app-section');
    });

    choiceSkillGapBtn.addEventListener('click', () => {
        currentMode = 'skill-gap';
        appHeader.textContent = 'Skill Gap Analysis';
        jobTitleGroup.style.display = 'block';
        jobTitleInput.required = true;
        skillsInput.required = true;
        showPage('app-section');
    });

    // --- PDF Upload and Skill Extraction ---
    resumeInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file || file.type !== 'application/pdf') {
            uploadStatus.textContent = 'Please select a PDF file.';
            return;
        }
        uploadStatus.textContent = 'Reading PDF...';
        try {
            const pdfText = await extractTextFromPdf(file);
            uploadStatus.textContent = 'Extracting skills from text...';
            const skills = await extractSkillsFromText(pdfText);
            skillsInput.value = skills.join(', ');
            uploadStatus.textContent = `✅ Successfully extracted ${skills.length} skills!`;
        } catch (error) {
            console.error('Error during resume processing:', error);
            uploadStatus.textContent = `❌ ${error.message}`;
        }
    });

    // --- Form Submission (API Calls) ---
    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        loader.style.display = 'block';
        resultsList.innerHTML = '';

        const skillsList = skillsInput.value.split(',').map(skill => skill.trim()).filter(Boolean);
        let endpoint = '';
        let payload = {};

        if (currentMode === 'recommender') {
            endpoint = '/recommend/';
            payload = { user_skills: skillsList };
        } else if (currentMode === 'skill-gap') {
            endpoint = '/role-skill-gap/';
            payload = {
                user_skills: skillsList,
                job_title: jobTitleInput.value.trim(),
            };
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) throw new Error('Network response was not ok.');
            const data = await response.json();
            if (data.error) {
                displayError(data.error);
            } else {
                displayResults(data, skillsList);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            displayError(error.message);
        } finally {
            loader.style.display = 'none';
        }
    });

    // --- Helper & Display Functions ---
    async function extractTextFromPdf(file) {
        // This function uses pdf.js to read text from a PDF file
        const reader = new FileReader();
        return new Promise((resolve, reject) => {
            reader.onload = async () => {
                try {
                    const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(reader.result) }).promise;
                    let fullText = '';
                    for (let i = 1; i <= pdf.numPages; i++) {
                        const page = await pdf.getPage(i);
                        const textContent = await page.getTextContent();
                        fullText += textContent.items.map(item => item.str).join(' ') + '\n';
                    }
                    resolve(fullText);
                } catch (error) {
                    reject(new Error('Could not parse PDF file.'));
                }
            };
            reader.readAsArrayBuffer(file);
        });
    }

    async function extractSkillsFromText(text) {
        // This function calls our backend skill extractor
        const response = await fetch(`${API_URL}/extract-skills/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });
        if (!response.ok) throw new Error('Backend could not extract skills.');
        const data = await response.json();
        return data.extracted_skills || [];
    }
    
    function displayResults(results, userSkills) {
    if (!results || results.length === 0) {
        resultsList.innerHTML = '<li>No matching jobs found. Try a different search.</li>';
        return;
    }

    results.forEach(job => {
        const jobCard = document.createElement('li');
        jobCard.className = 'job-card';

        let matching_skills, missing_skills;

        // --- THE FIX IS HERE ---
        // Check if the API response already includes the skill gap analysis.
        if (job.matching_skills !== undefined && job.missing_skills !== undefined) {
            // Case 1: Data is from /role-skill-gap/, so we use it directly.
            matching_skills = job.matching_skills;
            missing_skills = job.missing_skills;
        } else {
            // Case 2: Data is from /recommend/, so we calculate the gap here.
            const userSkillSet = new Set(userSkills.map(s => s.toLowerCase()));
            const requiredSkills = new Set((job.skills_list || []).map(s => s.toLowerCase()));
            
            matching_skills = [...userSkillSet].filter(s => requiredSkills.has(s));
            missing_skills = [...requiredSkills].filter(s => !userSkillSet.has(s));
        }
        // -----------------------

        const haveSkills = matching_skills.join(', ') || 'None';
        const needSkills = missing_skills.join(', ') || 'None!';

        jobCard.innerHTML = `
            <h3>${job.job_title}</h3>
            <p class="company-name">${job.company}</p>
            <div class="skill-gap">
                <div class="skills-have">
                    <strong>✅ Skills You Have (${matching_skills.length}):</strong>
                    <p>${haveSkills}</p>
                </div>
                <div class="skills-needed">
                    <strong>❌ Skills You Need (${missing_skills.length}):</strong>
                    <p>${needSkills}</p>
                </div>
            </div>
            <a href="${job.job_link}" target="_blank" rel="noopener noreferrer" class="job-link-button">
                View Original Job Posting
            </a>
        `;
        resultsList.appendChild(jobCard);
    });
}

    function displayError(message) {
        resultsList.innerHTML = `<li class="error-card">${message}</li>`;
    }
});