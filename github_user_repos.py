import csv
import json
import requests
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

def export_to_csv(repos: List[Dict[str, Any]], filename: str) -> None:
    fieldnames = [
        "name",
        "description",
        "main_language",
        "stars",
        "forks",
        "creation_date",
        "last_update_date"
    ]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repos)

if __name__ == "__main__":
    target_user = input("Enter GitHub username: ").strip()
    pat_token = input("Enter Personal Access Token (optional, press Enter to skip): ").strip() or None
    
    if target_user:
        print(f"\nFetching repositories for '{target_user}'...")
        repositories = fetch_github_user_repos(target_user, pat_token)
        print(f"Total repositories found: {len(repositories)}")
        
        if repositories:
            csv_filename = f"{target_user}_repos.csv"
            export_to_csv(repositories, csv_filename)
            print(f"Successfully exported data to '{csv_filename}'.\n")
            
            print("Preview of fetched repositories:")
            print(json.dumps(repositories[:2], indent=2))
