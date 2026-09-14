import csv
import json
import logging
import sqlite3
import time
import requests
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def fetch_with_retry(
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any],
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    timeout: float = 10.0
) -> Optional[requests.Response]:

    backoff = initial_backoff
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code in (403, 429):
                retry_after = response.headers.get("Retry-After")
                ratelimit_remaining = response.headers.get("X-RateLimit-Remaining")
                ratelimit_reset = response.headers.get("X-RateLimit-Reset")
                
                if retry_after and retry_after.isdigit():
                    wait_time = float(retry_after)
                    logging.warning(f"Rate limited (HTTP {response.status_code}). 'Retry-After' requested wait: {wait_time}s.")
                elif ratelimit_remaining == "0" and ratelimit_reset and ratelimit_reset.isdigit():
                    now = time.time()
                    reset_timestamp = float(ratelimit_reset)
                    wait_time = max(reset_timestamp - now + 1, backoff)
                    logging.warning(f"Primary rate limit exhausted. Waiting until reset timestamp ({wait_time:.1f}s).")
                else:
                    wait_time = backoff
                    logging.warning(f"HTTP {response.status_code} received on attempt {attempt}/{max_retries}. Backing off for {wait_time:.1f}s.")
                
                if attempt < max_retries:
                    time.sleep(wait_time)
                    backoff *= 2
                    continue

            elif response.status_code in (500, 502, 503, 504):
                logging.warning(f"Server error HTTP {response.status_code} on attempt {attempt}/{max_retries}. Retrying in {backoff:.1f}s...")
                if attempt < max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue

            return response

        except requests.exceptions.RequestException as req_err:
            logging.warning(f"Network error on attempt {attempt}/{max_retries}: {req_err}")
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
            else:
                logging.error(f"Max retries ({max_retries}) reached for URL {url}.")
                return None
                
    return None

def fetch_github_user_repos(
    username: str,
    token: Optional[str] = None,
    max_retries: int = 5
) -> Tuple[List[Dict[str, Any]], int]:

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
        response = fetch_with_retry(url, headers, params, max_retries=max_retries)
        
        if not response:
            logging.error(f"Failed to retrieve page {page} due to repeated network or rate limit errors.")
            break
            
        if response.status_code == 404:
            logging.error(f"User '{username}' not found (HTTP 404).")
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

def export_to_sqlite(repos: List[Dict[str, Any]], db_filename: str, table_name: str = "repositories") -> int:
    inserted_count = 0
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            main_language TEXT,
            stars INTEGER,
            forks INTEGER,
            creation_date TEXT,
            last_update_date TEXT
        );
        """
        cursor.execute(create_table_query)
        
        insert_query = f"""
        INSERT OR REPLACE INTO {table_name} (
            name, description, main_language, stars, forks, creation_date, last_update_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        
        for repo in repos:
            cursor.execute(insert_query, (
                repo.get("name"),
                repo.get("description"),
                repo.get("main_language"),
                repo.get("stars"),
                repo.get("forks"),
                repo.get("creation_date"),
                repo.get("last_update_date")
            ))
            inserted_count += 1
            
        conn.commit()
        conn.close()
        logging.info(f"Successfully exported {inserted_count} repository records to SQLite database '{db_filename}' (table: '{table_name}').")
    except sqlite3.Error as sql_err:
        logging.error(f"Failed to write to SQLite database '{db_filename}': {sql_err}")
        
    return inserted_count

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
            db_filename = f"{target_user}_repos.db"
            
            csv_count = export_to_csv(repositories, csv_filename)
            sqlite_count = export_to_sqlite(repositories, db_filename)
            
            print(f"Total Records Written to CSV ({csv_filename}): {csv_count}")
            print(f"Total Records Written to SQLite DB ({db_filename}): {sqlite_count}\n")
            
            print("Preview of fetched repositories:")
            print(json.dumps(repositories[:2], indent=2))
        else:
            logging.warning("No repositories were retrieved or processed.")
