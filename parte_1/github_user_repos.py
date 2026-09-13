import csv
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def fetch_github_user_repos(username: str, token: Optional[str] = None) -> Tuple[List[Dict[str, Any]], int]:
    url = f"https://api.github.com/users/{username}/repos"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHub-User-Repo-Fetcher"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    repos_data = []
    processed_count = 0
    page = 1
    per_page = 100
    
    while True:
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "full_name",
            "direction": "asc"
        }
        
        logging.info(f"Fetching page {page} for user '{username}'...")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 404:
                logging.error(f"User '{username}' not found (HTTP 404).")
                break
            elif response.status_code == 403:
                rate_limit_reset = response.headers.get("X-RateLimit-Reset", "unknown")
                logging.error(f"Access forbidden / Rate limit exceeded (HTTP 403). Reset timestamp: {rate_limit_reset}")
                break
            elif response.status_code != 200:
                error_msg = response.json().get('message', 'Failed to fetch repositories') if response.content else response.reason
                logging.error(f"HTTP Error {response.status_code}: {error_msg}")
                break
                
            page_repos = response.json()
            if not page_repos:
                logging.info("No more repositories found.")
                break
                
            for repo in page_repos:
                try:
                    repo_info = {
                        "name": repo.get("name"),
                        "description": repo.get("description"),
                        "main_language": repo.get("language"),
                        "stars": repo.get("stargazers_count"),
                        "forks": repo.get("forks_count"),
                        "creation_date": repo.get("created_at"),
                        "last_update_date": repo.get("updated_at")
                    }
                    repos_data.append(repo_info)
                    processed_count += 1
                except Exception as parse_err:
                    logging.error(f"Error processing repository '{repo.get('name', 'unknown')}': {parse_err}")
                
            if len(page_repos) < per_page:
                break
                
            page += 1

        except requests.exceptions.RequestException as req_err:
            logging.error(f"Network request failed on page {page}: {req_err}")
            break

    logging.info(f"Finished fetching. Total repositories processed: {processed_count}")
    return repos_data, processed_count

def export_to_csv(repos: List[Dict[str, Any]], filename: str) -> int:
    fieldnames = [
        "name",
        "description",
        "main_language",
        "stars",
        "forks",
        "creation_date",
        "last_update_date"
    ]
    
    written_count = 0
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for repo in repos:
                writer.writerow(repo)
                written_count += 1
        logging.info(f"Successfully exported {written_count} repository records to '{filename}'.")
    except IOError as io_err:
        logging.error(f"Failed to write CSV file '{filename}': {io_err}")
        
    return written_count

if __name__ == "__main__":
    target_user = input("Enter GitHub username: ").strip()
    pat_token = input("Enter Personal Access Token (optional, press Enter to skip): ").strip() or None
    
    if target_user:
        logging.info(f"Starting repository retrieval process for '{target_user}'...")
        repositories, total_processed = fetch_github_user_repos(target_user, pat_token)
        
        print("\n--- Summary Report ---")
        print(f"User: {target_user}")
        print(f"Total Repositories Processed: {total_processed}")
        
        if repositories:
            csv_filename = f"{target_user}_repos.csv"
            exported_count = export_to_csv(repositories, csv_filename)
            print(f"Total Records Written to CSV: {exported_count}\n")
            
            print("Preview of fetched repositories:")
            print(json.dumps(repositories[:2], indent=2))
        else:
            logging.warning("No repositories were retrieved or processed.")
