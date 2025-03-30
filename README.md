# LeetCode Stats API

A robust RESTful API to fetch and display LeetCode statistics for users, built with Flask.
hosted at [leetcode-stats.tashif.codes](https://leetcode-stats.tashif.codes)

## Features

- Retrieve user's solved problems count (easy, medium, hard)
- Get detailed submission statistics
- View contest ratings and historical rankings
- Track progress over time
- Easy integration with other applications
- Rate-limited endpoints to prevent abuse

## API Endpoints

### Get User Statistics

```
GET /{username}
```

Retrieves the basic statistics for a LeetCode user.

#### Parameters

- `username` (path): LeetCode username

#### Response

Returns user's LeetCode statistics including:

- Total solved problems (by difficulty)
- Acceptance rate
- Submission counts
- Ranking
- Contribution points
- Reputation
- Submission calendar

#### Example Response

```json
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
	"submissionCalendar": { "timestamp": "count" }
}
```

### Get Contest Rankings

```
GET /{username}/contests
```

Retrieves the user's contest history and rankings.

#### Parameters

- `username` (path): LeetCode username

#### Response

Returns:

- Contest participation statistics
- Global ranking
- Contest history with details for each contest

#### Example Response

```json
{
	"status": "success",
	"message": "retrieved",
	"attendedContestsCount": 10,
	"rating": 1500,
	"globalRanking": 5000,
	"totalParticipants": 100000,
	"topPercentage": 5.0,
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
```

### Get User Profile

```
GET /{username}/profile
```

Retrieves detailed profile information for a user.

#### Parameters

- `username` (path): LeetCode username

#### Response

Returns:

- Personal profile information
- Social media links
- Contributions
- Skills
- Recent submissions

#### Example Response

```json
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
	"badges": [],
	"upcomingBadges": [],
	"activeBadge": {},
	"submitStats": {},
	"submissionCalendar": { "timestamp": "count" },
	"recentSubmissions": []
}
```

### Get User Badges

```
GET /{username}/badges
```

Retrieves badges earned by the user.

#### Parameters

- `username` (path): LeetCode username

#### Response

Returns:

- List of earned badges
- Upcoming badges
- Current active badge

#### Example Response

```json
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
```

## API Documentation

Detailed API documentation is available when the server is running by visiting:

```
GET /docs
```

This provides an interactive documentation page with detailed information about all endpoints, parameters, and example responses.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Request successful
- `404 Not Found`: User not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

Error responses follow this format:

```json
{
	"status": "error",
	"message": "error description"
}
```

## Usage Examples

### Python

```python
import requests

username = "leetcoder"
response = requests.get(f"https://leetcode-stats.tashif.codes/{username}")
data = response.json()

print(f"{username} has solved {data['totalSolved']} problems!")
```

### JavaScript

```javascript
fetch(`https://leetcode-stats.tashif.codes/${username}`)
	.then((response) => response.json())
	.then((data) => console.log(data));
```

## Installation

### Setup

1. Clone the repository

   ```bash
   git clone https://github.com/tashifkhan/LeetCode-Stats-API.git
   cd LeetCode-Stats-API
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Start the server
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:58352`.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

Full API documentation is available at `/` endpoints when the server is running.

## License

MIT License. See [LICENSE](LICENSE) for more information.
