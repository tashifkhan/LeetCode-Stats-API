from flask import Blueprint, render_template_string

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/")
def docs():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LeetCode Stats API Documentation</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
            <style>
                :root {
                    --primary-color: #e4e4e4;
                    --secondary-color: #64ffda;
                    --background-color: #0a192f;
                    --code-background: #112240;
                    --text-color: #8892b0;
                    --heading-color: #ccd6f6;
                    --card-background: #112240;
                    --hover-color: #233554;
                }
                body {
                    font-family: 'SF Mono', 'Fira Code', 'Monaco', monospace;
                    line-height: 1.6;
                    color: var(--text-color);
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 4rem 2rem;
                    background: var(--background-color);
                    transition: all 0.25s ease-in-out;
                }
                h1, h2, h3 {
                    color: var(--heading-color);
                    padding-bottom: 0.75rem;
                    margin-top: 2rem;
                    font-weight: 600;
                    letter-spacing: -0.5px;
                }
                h1 {
                    font-size: clamp(1.8rem, 4vw, 2.5rem);
                    margin-bottom: 2rem;
                    border-bottom: 2px solid var(--secondary-color);
                }
                .endpoint {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 0;
                    margin: 1.5rem 0;
                    box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7);
                    border: 1px solid var(--hover-color);
                    transition: all 0.2s ease-in-out;
                    overflow: hidden;
                }
                .endpoint-header {
                    padding: 1.5rem;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: background-color 0.2s ease;
                }
                .endpoint-header:hover {
                    background-color: var(--hover-color);
                }
                .endpoint-header h2 {
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                .endpoint-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                    padding: 0 1.5rem;
                }
                .endpoint.active .endpoint-content {
                    max-height: 5000px; /* Large enough to show all content */
                    padding: 0 1.5rem 1.5rem;
                }
                .endpoint-toggle {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--secondary-color);
                    transition: transform 0.3s ease;
                }
                .endpoint.active .endpoint-toggle {
                    transform: rotate(45deg);
                }
                code {
                    background: var(--code-background);
                    color: var(--secondary-color);
                    padding: 0.3rem 0.6rem;
                    border-radius: 6px;
                    font-family: 'SF Mono', 'Fira Code', monospace;
                    font-size: 0.85em;
                    word-break: break-word;
                    white-space: pre-wrap;
                }
                pre {
                    background: var(--code-background);
                    padding: 1.5rem;
                    border-radius: 12px;
                    overflow-x: auto;
                    margin: 1.5rem 0;
                    border: 1px solid var(--hover-color);
                    position: relative;
                }
                pre code {
                    padding: 0;
                    background: none;
                    color: var(--primary-color);
                    font-size: 0.9em;
                }
                .parameter {
                    margin: 1.5rem 0;
                    padding: 1.25rem;
                    border-left: 4px solid var(--secondary-color);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 4px 12px -6px rgba(2,12,27,0.4);
                    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                }
                .parameter:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px -6px rgba(2,12,27,0.5);
                }
                .parameter code {
                    font-size: 0.95em;
                    font-weight: 500;
                    margin-right: 0.5rem;
                }
                .error-response {
                    border-left: 4px solid #ff79c6;
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    overflow-x: auto;
                }
                .note {
                    background: var(--hover-color);
                    border-left: 4px solid var(--secondary-color);
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    border-radius: 0 8px 8px 0;
                }
                footer {
                    margin-top: 3rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid var(--hover-color);
                    text-align: center;
                    color: var(--text-color);
                    font-size: 0.9em;
                }
                p {
                    margin: 1.25rem 0;
                    font-size: 1rem;
                    line-height: 1.7;
                }
                @media (max-width: 768px) {
                    body {
                        padding: 1rem 0.75rem;
                    }
                    .endpoint-header {
                        padding: 1.25rem;
                    }
                    pre {
                        padding: 1rem;
                        font-size: 0.9em;
                    }
                    code {
                        font-size: 0.8em;
                    }
                }
                @media (max-width: 480px) {
                    body {
                        padding: 1rem 0.5rem;
                    }
                    .endpoint-header {
                        padding: 1rem;
                    }
                    h1 {
                        font-size: 1.8rem;
                    }
                    pre {
                        padding: 0.75rem;
                        font-size: 0.85em;
                    }
                    .parameter, .error-response, .note {
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                }
                .method {
                    color: #ff79c6;
                    font-weight: bold;
                }
                .path {
                    color: var(--secondary-color);
                }
                .parameter {
                    margin: 1rem 0 1rem 1.5rem;
                    padding: 1rem;
                    border-left: 3px solid var(--secondary-color);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                }
                .error-section {
                    margin: 2rem 0;
                }
                .error-section h2 {
                    border-bottom: 2px solid var(--secondary-color);
                    padding-bottom: 0.75rem;
                }
                .error-toggle {
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem;
                    background: var(--card-background);
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    border: 1px solid var(--hover-color);
                }
                .error-toggle:hover {
                    background: var(--hover-color);
                }
                .error-toggle h3 {
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                .error-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                }
                .error-item.active .error-content {
                    max-height: 1000px;
                }
                .error-toggle-icon {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--secondary-color);
                    transition: transform 0.3s ease;
                }
                .error-item.active .error-toggle-icon {
                    transform: rotate(45deg);
                }
                ::selection {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .endpoint-method {
                    display: inline-block;
                    padding: 0.3rem 0.5rem;
                    background: #ff79c6;
                    color: var(--background-color);
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 0.5rem;
                }
                /* LeetCode Profile Analyzer styles */
                .analyzer-form {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 2rem;
                    margin: 2rem 0;
                    border: 1px solid var(--hover-color);
                    text-align: center;
                }
                .analyzer-form h3 {
                    margin-bottom: 1.5rem;
                    color: var(--heading-color);
                }
                .input-group {
                    display: flex;
                    gap: 1rem;
                    max-width: 500px;
                    margin: 0 auto;
                }
                .input-group input {
                    flex: 1;
                    padding: 0.75rem 1rem;
                    border: 2px solid var(--hover-color);
                    border-radius: 8px;
                    background: var(--code-background);
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 1rem;
                    transition: border-color 0.2s ease;
                }
                .input-group input:focus {
                    outline: none;
                    border-color: var(--secondary-color);
                }
                .analyze-button {
                    padding: 0.75rem 1.5rem;
                    background: var(--secondary-color);
                    color: var(--background-color);
                    border: none;
                    border-radius: 8px;
                    font-family: inherit;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                .analyze-button:hover {
                    background: #4cd4b0;
                    transform: translateY(-2px);
                }
                .loading {
                    text-align: center;
                    margin: 2rem 0;
                }
                .spinner {
                    width: 40px;
                    height: 40px;
                    border: 4px solid var(--hover-color);
                    border-top: 4px solid var(--secondary-color);
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .profile-results {
                    margin-top: 2rem;
                }
                .profile-section {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 2rem;
                    margin: 2rem 0;
                    border: 1px solid var(--hover-color);
                }
                .profile-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1.5rem;
                }
                .profile-card {
                    background: var(--hover-color);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .profile-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 25px rgba(2,12,27,0.3);
                }
                .card-content h4 {
                    color: var(--text-color);
                    margin-bottom: 0.5rem;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .card-value {
                    color: var(--secondary-color);
                    font-size: 2rem;
                    font-weight: 700;
                }
                @media (max-width: 768px) {
                    .input-group {
                        flex-direction: column;
                    }
                    .profile-cards {
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    }
                }
            </style>
        </head>
        <body>
            <h1>LeetCode Profile Analyzer</h1>
            <div class="analyzer-form">
                <h3>Analyze a LeetCode Profile</h3>
                <div class="input-group">
                    <input type="text" id="leetcode-username" placeholder="Enter LeetCode username (e.g., khan-tashif)" />
                    <button onclick="analyzeLeetCodeUser()" class="analyze-button">Analyze</button>
                </div>
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Fetching LeetCode data...</p>
                </div>
            </div>
            <div id="profile-results" class="profile-results" style="display: none;">
                <div class="profile-section">
                    <h3>Profile Overview</h3>
                    <div id="user-info-card" class="profile-card" style="max-width: 500px; margin: 0 auto 2rem auto; text-align: left;"></div>
                    <div class="profile-cards">
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Total Solved</h4>
                                <div id="total-solved" class="card-value">-</div>
                            </div>
                        </div>
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Acceptance Rate</h4>
                                <div id="acceptance-rate" class="card-value">-</div>
                            </div>
                        </div>
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Ranking</h4>
                                <div id="ranking" class="card-value">-</div>
                            </div>
                        </div>
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Contests Attended</h4>
                                <div id="contests-attended" class="card-value">-</div>
                            </div>
                        </div>
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Contest Rating</h4>
                                <div id="contest-rating" class="card-value">-</div>
                            </div>
                        </div>
                        <div class="profile-card">
                            <div class="card-content">
                                <h4>Badges</h4>
                                <div id="badges-count" class="card-value">-</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script>
                async function analyzeLeetCodeUser() {
                    const usernameInput = document.getElementById('leetcode-username');
                    const username = usernameInput.value.trim();
                    if (!username) {
                        alert('Please enter a LeetCode username');
                        return;
                    }
                    const loading = document.getElementById('loading');
                    const results = document.getElementById('profile-results');
                    loading.style.display = 'block';
                    results.style.display = 'none';
                    try {
                        const [statsRes, contestsRes, badgesRes, profileRes] = await Promise.all([
                            fetch(`/${username}`),
                            fetch(`/${username}/contests`),
                            fetch(`/${username}/badges`),
                            fetch(`/${username}/profile`)
                        ]);
                        const stats = await statsRes.json();
                        const contests = await contestsRes.json();
                        const badges = await badgesRes.json();
                        const profile = await profileRes.json();
                        // Fill in the cards
                        document.getElementById('total-solved').textContent = stats.totalSolved ?? '-';
                        document.getElementById('acceptance-rate').textContent = stats.acceptanceRate ? stats.acceptanceRate + '%' : '-';
                        document.getElementById('ranking').textContent = stats.ranking ?? '-';
                        document.getElementById('contests-attended').textContent = contests.attendedContestsCount ?? '-';
                        document.getElementById('contest-rating').textContent = contests.rating ?? '-';
                        document.getElementById('badges-count').textContent = badges.badges ? badges.badges.length : '-';
                        // Render user info
                        renderUserInfoCard(profile);
                        results.style.display = 'block';
                    } catch (e) {
                        alert('Failed to fetch LeetCode data. Please check the username and try again.');
                    } finally {
                        loading.style.display = 'none';
                    }
                }
                function renderUserInfoCard(profile) {
                    const card = document.getElementById('user-info-card');
                    if (!profile || !profile.profile) {
                        card.innerHTML = '<div style="color: var(--text-color);">No user info available.</div>';
                        return;
                    }
                    const p = profile.profile;
                    const contrib = profile.contributions || {};
                    let html = `<div style="display: flex; align-items: center; gap: 1.5rem;">
                        <img src="${p.userAvatar}" alt="avatar" style="width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--secondary-color); background: #fff; object-fit: cover;">
                        <div>
                            <div style="font-size: 1.3rem; color: var(--heading-color); font-weight: 600;">${p.realName || profile.username}</div>
                            <div style="color: var(--secondary-color); font-size: 1rem;">@${profile.username}</div>
                            ${p.countryName ? `<div style='margin-top: 0.2rem;'>${p.countryName}</div>` : ''}
                            ${p.company ? `<div style='margin-top: 0.2rem;'>🏢 ${p.company}</div>` : ''}
                            ${p.school ? `<div style='margin-top: 0.2rem;'>🎓 ${p.school}</div>` : ''}
                        </div>
                    </div>`;
                    html += `<div style="margin-top: 1rem;">
                        ${p.skillTags && p.skillTags.length ? `<div><b>Skills:</b> ${p.skillTags.join(', ')}</div>` : ''}
                        ${p.aboutMe ? `<div style='margin-top: 0.5rem;'><b>About:</b> ${p.aboutMe}</div>` : ''}
                        <div style='margin-top: 0.5rem;'><b>Contribution Points:</b> ${contrib.points ?? 0}, <b>Questions:</b> ${contrib.questionCount ?? 0}, <b>Testcases:</b> ${contrib.testcaseCount ?? 0}</div>
                        <div style='margin-top: 0.5rem;'>
                            ${profile.githubUrl ? `<a href='${profile.githubUrl}' target='_blank' style='color: var(--secondary-color); margin-right: 1rem;'>GitHub</a>` : ''}
                            ${profile.twitterUrl ? `<a href='${profile.twitterUrl}' target='_blank' style='color: var(--secondary-color); margin-right: 1rem;'>Twitter</a>` : ''}
                            ${profile.linkedinUrl ? `<a href='${profile.linkedinUrl}' target='_blank' style='color: var(--secondary-color);'>LinkedIn</a>` : ''}
                        </div>
                    </div>`;
                    card.innerHTML = html;
                }
                // Allow Enter key to submit form
                document.addEventListener('DOMContentLoaded', function() {
                    const input = document.getElementById('leetcode-username');
                    if (input) {
                        input.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                analyzeLeetCodeUser();
                            }
                        });
                    }
                });
            </script>
            <h1>LeetCode Stats API Documentation</h1>
            
            <p>This API provides access to LeetCode user statistics and submission data. Click on each endpoint to see details.</p>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Statistics</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{username}</span></code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>username</code> (path parameter): LeetCode username
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "status": "success",
    "message": "retrieved",
    "totalSolved": 100,
    "totalQuestions": 2000,
    "easySolved": 40,
    "totalEasy": 500,
    "mediumSolved": 40,
    "totalMedium": 1000,
    "hardSolved": 20,
    "totalHard": 500,
    "acceptanceRate": 65.5,
    "ranking": 100000,
    "contributionPoints": 50,
    "reputation": 100,
    "submissionCalendar": {"timestamp": "count"}
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /khan-tashif</code></pre>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> Contest Rankings</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{username}</span>/contests</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>username</code> (path parameter): LeetCode username
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "status": "success",
    "message": "retrieved",
    "attendedContestsCount": 10,
    "rating": 1500,
    "globalRanking": 5000,
    "totalParticipants": 100000,
    "topPercentage": 5.00,
    "badge": {
        "name": "Guardian"
    },
    "contestHistory": [
        {
            "attended": true,
            "rating": 1500,
            "ranking": 1000,
            "trendDirection": "UP",
            "problemsSolved": 3,
            "totalProblems": 4,
            "finishTimeInSeconds": 3600,
            "contest": {
                "title": "Weekly Contest 123",
                "startTime": 1615694400
            }
        }
    ]
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /khan-tashif/contests</code></pre>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Profile</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{username}</span>/profile</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>username</code> (path parameter): LeetCode username
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "status": "success",
    "message": "retrieved",
    "username": "example_user",
    "githubUrl": "https://github.com/example",
    "twitterUrl": "https://twitter.com/example",
    "linkedinUrl": "https://linkedin.com/in/example",
    "contributions": {
        "points": 100,
        "questionCount": 5,
        "testcaseCount": 10
    },
    "profile": {
        "realName": "Example User",
        "userAvatar": "https://assets.leetcode.com/avatar.jpg",
        "birthday": "2000-01-01",
        "ranking": 10000,
        "reputation": 100,
        "websites": ["https://example.com"],
        "countryName": "United States",
        "company": "Example Corp",
        "school": "Example University",
        "skillTags": ["Python", "Algorithms"],
        "aboutMe": "LeetCode enthusiast",
        "starRating": 4.5
    },
    "badges": [...],
    "upcomingBadges": [...],
    "activeBadge": {...},
    "submitStats": {...},
    "submissionCalendar": {"timestamp": "count"},
    "recentSubmissions": [...]
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /khan-tashif/profile</code></pre>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Badges</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{username}</span>/badges</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>username</code> (path parameter): LeetCode username
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "status": "success",
    "message": "retrieved",
    "badges": [
        {
            "id": "1",
            "displayName": "Problem Solver",
            "icon": "badge-icon-url",
            "creationDate": 1609459200
        }
    ],
    "upcomingBadges": [
        {
            "name": "Fast Coder",
            "icon": "upcoming-badge-icon-url"
        }
    ],
    "activeBadge": {
        "id": "1",
        "displayName": "Problem Solver",
        "icon": "badge-icon-url",
        "creationDate": 1609459200
    }
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /khan-tashif/badges</code></pre>
                </div>
            </div>

            <div class="error-section">
                <h2>Error Responses</h2>
                
                <div class="error-item">
                    <div class="error-toggle">
                        <h3>User not found</h3>
                        <span class="error-toggle-icon">+</span>
                    </div>
                    <div class="error-content">
                        <pre>
<code>{
    "status": "error",
    "message": "user does not exist",
    ...
}</code>
                        </pre>
                    </div>
                </div>

                <div class="error-item">
                    <div class="error-toggle">
                        <h3>Server error</h3>
                        <span class="error-toggle-icon">+</span>
                    </div>
                    <div class="error-content">
                        <pre>
<code>
{
    "status": "error",
    "message": "error message",
    ...
}
</code>
                        </pre>
                    </div>
                </div>
            </div>

            <div class="note">
                <h2>Rate Limiting</h2>
                <p>Please be mindful of LeetCode's rate limiting policies when using this API.</p>
            </div>

            <footer>
                <p>This API is open source and available on <a href="https://github.com/tashifkhan/LeetCode-Stats-API" style="color: var(--secondary-color); text-decoration: none;">GitHub</a>.</p>
                <p>Try it live at <a href="https://leetcode-stats.tashif.codes" style="color: var(--secondary-color); text-decoration: none;">leetcode-stats.tashif.codes</a></p>
            </footer>

            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Handle endpoint toggles
                    const endpoints = document.querySelectorAll('.endpoint');
                    endpoints.forEach(endpoint => {
                        const header = endpoint.querySelector('.endpoint-header');
                        header.addEventListener('click', () => {
                            endpoint.classList.toggle('active');
                        });
                    });
                    
                    // Handle error toggles
                    const errorItems = document.querySelectorAll('.error-item');
                    errorItems.forEach(item => {
                        const toggle = item.querySelector('.error-toggle');
                        toggle.addEventListener('click', () => {
                            item.classList.toggle('active');
                        });
                    });
                    
                    // Make the first endpoint active by default for better UX
                    if (endpoints.length > 0) {
                        endpoints[0].classList.add('active');
                    }
                });
            </script>
        </body>
        </html>
    """
    return render_template_string(html)
