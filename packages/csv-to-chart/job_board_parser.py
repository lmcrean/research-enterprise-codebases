"""Parser for job board data from CSV."""

import csv
from pathlib import Path
from typing import Dict, List, Tuple


def parse_job_board_csv(file_path: str) -> Dict[str, Dict[str, int]]:
    """Parse job board CSV data into structured format.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with structure: {board_name: {keyword: count}}
    """
    data = {
        'LinkedIn': {},
        'TotalJobs': {},
        'CWJobs': {}
    }
    
    current_board = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Detect board sections
        if 'LINKEDIN' in line.upper():
            current_board = 'LinkedIn'
            continue
        elif 'TOTALJOBS' in line.upper():
            current_board = 'TotalJobs'
            continue
        elif 'CWJOBS' in line.upper():
            current_board = 'CWJobs'
            continue
        
        # Skip headers and URLs
        if 'location' in line.lower() or 'http' in line or 'travel from' in line.lower():
            continue
        
        # Parse data lines
        if current_board and ',' in line:
            parts = line.split(',')
            if len(parts) >= 2:
                keyword = parts[0].strip().lower()
                try:
                    count = int(parts[1].strip())
                    data[current_board][keyword] = count
                except (ValueError, IndexError):
                    continue
    
    return data


def categorize_keywords(data: Dict[str, Dict[str, int]]) -> Tuple[Dict, Dict, Dict]:
    """Categorize keywords into job titles and technologies.
    
    Args:
        data: Parsed job board data
        
    Returns:
        Tuple of (all_data, job_titles_data, tech_lang_data)
    """
    job_title_keywords = {
        'software engineer', 'web developer', 'devops', 'dev ops',
        'developer operations', 'data analyst', 'software developer',
        'data scientist', 'cyber security'
    }
    
    tech_lang_keywords = {
        'python', 'typescript', 'javascript', 'java', 'c#', 'csharp',
        'aws', 'kubernetes', 'docker', 'azure', 'gcp'
    }
    
    all_data = {}
    job_titles = {}
    tech_lang = {}
    
    for board, keywords in data.items():
        all_data[board] = {}
        job_titles[board] = {}
        tech_lang[board] = {}
        
        for keyword, count in keywords.items():
            # Normalize keyword for matching
            normalized = keyword.lower().strip()
            
            # Add to all data
            all_data[board][keyword] = count
            
            # Categorize
            if normalized in job_title_keywords:
                job_titles[board][keyword] = count
            elif normalized in tech_lang_keywords:
                tech_lang[board][keyword] = count
            # Check for partial matches in job titles
            elif any(title in normalized for title in ['engineer', 'developer', 'analyst', 'scientist']):
                job_titles[board][keyword] = count
            # Default remaining to tech/lang if not clearly a job title
            elif not any(title in normalized for title in ['operations']):
                tech_lang[board][keyword] = count
    
    return all_data, job_titles, tech_lang


def get_sorted_categories(data: Dict[str, Dict[str, int]]) -> List[str]:
    """Get categories sorted by total count across all boards.
    
    Args:
        data: Categorized data {board: {keyword: count}}
        
    Returns:
        List of keywords sorted by total count (descending)
    """
    totals = {}
    
    for board_data in data.values():
        for keyword, count in board_data.items():
            totals[keyword] = totals.get(keyword, 0) + count
    
    return sorted(totals.keys(), key=lambda x: totals[x], reverse=True)