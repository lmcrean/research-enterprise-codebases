#!/usr/bin/env python3
"""Test script to verify GitHub API count functions are working correctly"""

import requests
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def get_contributors_count(owner, repo, headers):
    """Get the number of contributors for a repository"""
    try:
        # GitHub API has a max of 500 contributors returned
        # For accurate count, we need to check pagination
        contributors_url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100&anon=true'
        response = requests.get(contributors_url, headers=headers)
        
        if response.status_code == 200:
            contributors = response.json()
            total_count = len(contributors)
            
            # Check if there are more pages
            if 'Link' in response.headers:
                link_header = response.headers['Link']
                # Parse the last page number from Link header
                last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if last_page_match:
                    last_page = int(last_page_match.group(1))
                    # Get the last page to count remaining contributors
                    last_page_url = f'{contributors_url}&page={last_page}'
                    last_response = requests.get(last_page_url, headers=headers)
                    if last_response.status_code == 200:
                        last_page_contributors = len(last_response.json())
                        # Total = (pages - 1) * 100 + last page count
                        total_count = (last_page - 1) * 100 + last_page_contributors
            
            return total_count
        elif response.status_code == 403:
            # Repository might have disabled contributor stats
            return -1
        else:
            return -1
    except Exception as e:
        print(f"Error counting contributors for {owner}/{repo}: {str(e)}")
        return -1

def get_open_prs_count(owner, repo, headers):
    """Get the number of open pull requests"""
    try:
        # Use search API for accurate count (it returns total_count directly)
        search_url = f'https://api.github.com/search/issues?q=is:pr+is:open+repo:{owner}/{repo}'
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('total_count', 0)
        
        # Fallback to pulls endpoint if search fails
        prs_url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=open&per_page=100'
        response = requests.get(prs_url, headers=headers)
        
        if response.status_code == 200:
            prs = response.json()
            total_count = len(prs)
            
            # Check for pagination
            if 'Link' in response.headers:
                link_header = response.headers['Link']
                last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if last_page_match:
                    last_page = int(last_page_match.group(1))
                    # Get the last page to count remaining PRs
                    last_page_url = f'{prs_url}&page={last_page}'
                    last_response = requests.get(last_page_url, headers=headers)
                    if last_response.status_code == 200:
                        last_page_prs = len(last_response.json())
                        # Total = (pages - 1) * 100 + last page count
                        total_count = (last_page - 1) * 100 + last_page_prs
            
            return total_count
        else:
            return -1
    except Exception as e:
        print(f"Error counting PRs for {owner}/{repo}: {str(e)}")
        return -1

def test_repository(owner, repo, token=None):
    """Test a single repository"""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    print(f"\nTesting {owner}/{repo}:")
    print("-" * 50)
    
    # Get basic repo info
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        print(f"Repository: {repo_data['full_name']}")
        print(f"Stars: {repo_data['stargazers_count']:,}")
        print(f"Forks: {repo_data['forks_count']:,}")
        print(f"Open Issues: {repo_data['open_issues_count']:,}")
        
        # Test contributor count
        contributors = get_contributors_count(owner, repo, headers)
        print(f"Contributors: {contributors:,}" if contributors >= 0 else "Contributors: N/A")
        
        # Test PR count
        prs = get_open_prs_count(owner, repo, headers)
        print(f"Open PRs: {prs:,}" if prs >= 0 else "Open PRs: N/A")
    else:
        print(f"Failed to fetch repository info: {response.status_code}")

if __name__ == "__main__":
    # Get GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Warning: No GitHub token found. API rate limits will apply.")
    
    print("Testing GitHub API count functions")
    print("=" * 50)
    
    # Test repositories with different characteristics
    test_repos = [
        ("microsoft", "vscode"),      # Large repo with many contributors
        ("torvalds", "linux"),        # Very large repo
        ("pandas-dev", "pandas"),     # Medium repo
        ("gothinkster", "aspnetcore-realworld-example-app"),  # Small repo
    ]
    
    for owner, repo in test_repos:
        test_repository(owner, repo, github_token)
    
    print("\n" + "=" * 50)
    print("Test complete!")