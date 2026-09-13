import requests
import json
from typing import List, Dict, Any, Optional

def fetch_github_user_repos(username: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"https://api.github.com/users/{username}/repos"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHub-User-Repo-Fetcher"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    repos_data = []
    page = 1
    per_page = 100
    
    while True:
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "full_name",
            "direction": "asc"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 404:
            print(f"Error: User '{username}' not found.")
            break
        elif response.status_code != 200:
            print(f"Error {response.status_code}: {response.json().get('message', 'Failed to fetch repositories')}")
            break
            
        page_repos = response.json()
        if not page_repos:
            break
            
        for repo in page_repos:
            repos_data.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "main_language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "creation_date": repo.get("created_at"),
                "last_update_date": repo.get("updated_at")
            })
            
        if len(page_repos) < per_page:
            break
            
        page += 1

    return repos_data

if __name__ == "__main__":
    target_user = input("Enter GitHub username: ").strip()
    pat_token = input("Enter Personal Access Token (optional, press Enter to skip): ").strip() or None
    
    if target_user:
        print(f"\nFetching repositories for '{target_user}'...")
        repositories = fetch_github_user_repos(target_user, pat_token)
        print(f"Total repositories found: {len(repositories)}\n")
        
        print(json.dumps(repositories, indent=2))
