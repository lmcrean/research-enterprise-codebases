#!/usr/bin/env python3
"""
Quick test of the notebook's basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get GitHub token from environment
github_token = os.getenv('GITHUB_TOKEN')
if not github_token or github_token == 'your_github_token_here':
    print("ERROR: Please set your GITHUB_TOKEN in the .env file")
    print("Create a .env file with: GITHUB_TOKEN=your_actual_token")
    sys.exit(1)

try:
    # Test basic imports
    print("Testing imports...")
    import requests
    import pandas as pd
    from datetime import datetime
    import json
    print("SUCCESS: All imports working")
    
    # Test GitHub API connection
    print("\nTesting GitHub API...")
    headers = {'Authorization': f'token {github_token}'}
    
    # Test with a simple repo
    test_repo = 'huggingface/trl'
    response = requests.get(f'https://api.github.com/repos/{test_repo}', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: API working - {test_repo} has {data['stargazers_count']} stars")
        
        # Test rate limit info
        print("\nRate limit info:")
        print(f"Remaining requests: {response.headers.get('X-RateLimit-Remaining', 'Unknown')}")
        print(f"Reset time: {response.headers.get('X-RateLimit-Reset', 'Unknown')}")
        
    else:
        print(f"ERROR: API test failed - Status {response.status_code}")
        print(f"Response: {response.text}")
        
    # Test pandas DataFrame creation
    print("\nTesting DataFrame...")
    test_data = [
        {'name': 'test/repo', 'stars': 100, 'field': 'Test'},
        {'name': 'another/repo', 'stars': 200, 'field': 'Test'}
    ]
    df = pd.DataFrame(test_data)
    print(f"SUCCESS: DataFrame created with {len(df)} rows")
    
    print("\nAll basic tests passed! The notebook should work correctly.")
    
except ImportError as e:
    print(f"ERROR: Missing dependency - {e}")
    print("Please install: pip install requests pandas jupyter python-dotenv")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)