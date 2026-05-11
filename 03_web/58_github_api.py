"""
Script: GitHub API Client
What it does: Fetches public data from GitHub using their REST API.
No API key needed for public data (but there are rate limits).

Install: pip install requests
"""

try:
    import requests

    BASE = "https://api.github.com"
    HEADERS = {"Accept": "application/vnd.github.v3+json"}

    def get_user(username):
        """Fetch public profile info for a GitHub user."""
        response = requests.get(f"{BASE}/users/{username}", headers=HEADERS)
        if response.status_code == 404:
            return None
        return response.json()

    def get_repos(username, limit=5):
        """Get public repositories for a user."""
        response = requests.get(
            f"{BASE}/users/{username}/repos",
            headers=HEADERS,
            params={"sort": "stars", "per_page": limit}
        )
        return response.json()

    def search_repos(query, language=None, limit=5):
        """Search GitHub repositories by keyword."""
        q = query
        if language:
            q += f" language:{language}"
        response = requests.get(
            f"{BASE}/search/repositories",
            headers=HEADERS,
            params={"q": q, "per_page": limit, "sort": "stars"}
        )
        return response.json().get("items", [])

    # --- Get Python creator's profile ---
    print("=== GitHub User: python ===")
    user = get_user("python")
    if user:
        print(f"Name:       {user.get('name', 'N/A')}")
        print(f"Bio:        {user.get('bio', 'N/A')}")
        print(f"Public repos: {user.get('public_repos')}")
        print(f"Followers:  {user.get('followers'):,}")

    # --- Get top Python repos ---
    print("\n=== Top Python repos (by stars) ===")
    repos = get_repos("python", limit=5)
    for repo in repos:
        stars = repo.get("stargazers_count", 0)
        print(f"  ⭐ {stars:>6,} | {repo['name']} — {repo.get('description', '')[:50]}")

    # --- Search for beginner Python projects ---
    print("\n=== Top 'beginner python' repos ===")
    results = search_repos("beginner python tutorial", language="Python", limit=5)
    for repo in results:
        stars = repo.get("stargazers_count", 0)
        print(f"  ⭐ {stars:>6,} | {repo['full_name']} — {repo.get('description', '')[:50]}")

except ImportError:
    print("Install: pip install requests")
except Exception as e:
    print(f"Error: {e} (API rate limit may be reached)")
