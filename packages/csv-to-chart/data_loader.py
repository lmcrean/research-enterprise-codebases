"""Data loader module for CSV market share data."""

import os
import csv
from typing import Dict, List, Tuple


def load_csv_data(file_path: str) -> Tuple[List[float], List[float]]:
    """Load and parse CSV data from file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Tuple of (years, market_share_percentages)
    """
    years = []
    market_shares = []
    
    with open(file_path, 'r') as f:
        for line in f:
            # Clean and split the line
            line = line.strip()
            if not line:
                continue
                
            # Remove line numbers if present
            if '→' in line:
                data = line.split('→')[1]
            else:
                data = line
                
            # Parse comma-separated values
            parts = data.split(',')
            if len(parts) >= 2:
                try:
                    year = float(parts[0].strip())
                    market_share = float(parts[1].strip())
                    years.append(year)
                    market_shares.append(market_share)
                except ValueError:
                    continue
                    
    return years, market_shares


def load_all_datasets(data_dir: str) -> Dict[str, Tuple[List[float], List[float]]]:
    """Load all CSV files from the data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping technology names to (years, market_share) tuples
    """
    datasets = {}
    csv_files = [
        'artificial-intelligence.csv',
        'devops.csv',
        'machine-learning.csv',
        'software-engineering.csv',
        'web-development.csv'
    ]
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            tech_name = csv_file.replace('.csv', '').replace('-', ' ').title()
            datasets[tech_name] = load_csv_data(file_path)
            
    return datasets