from flask import Blueprint, render_template_string

docs_bp = Blueprint('docs', __name__)
@docs_bp.route('/')
def docs():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LeetCode Stats API Documentation</title>
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
            </style>
        </head>
        <body>
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