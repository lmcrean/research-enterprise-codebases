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
    
    # Load from themes subdirectory
    themes_files = [
        ('themes/artificial-intelligence.csv', 'Artificial Intelligence'),
        ('themes/machine-learning.csv', 'Machine Learning')
    ]
    
    # Load from job-title subdirectory
    job_title_files = [
        ('job-title/data-analytics.csv', 'Data Analytics'),
        ('job-title/data-science.csv', 'Data Science'),
        ('job-title/devops.csv', 'Devops'),
        ('job-title/software-engineering.csv', 'Software Engineering'),
        ('job-title/web-development.csv', 'Web Development')
    ]
    
    # Combine all files
    all_files = themes_files + job_title_files
    
    for csv_file, display_name in all_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            datasets[display_name] = load_csv_data(file_path)
        else:
            print(f"Warning: {csv_file} not found at {file_path}")
            
    return datasets


def load_language_datasets(data_dir: str) -> Dict[str, Tuple[List[float], List[float]]]:
    """Load programming language CSV files from the data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping language names to (years, market_share) tuples
    """
    datasets = {}
    language_files = [
        ('languages/csharp.csv', 'C#'),
        ('languages/java.csv', 'Java'),
        ('languages/javascript.csv', 'Javascript'),
        ('languages/python.csv', 'Python'),
        ('languages/typescript.csv', 'TypeScript')
    ]
    
    for csv_file, display_name in language_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            datasets[display_name] = load_csv_data(file_path)
        else:
            print(f"Warning: {csv_file} not found at {file_path}")
            
    return datasets


def load_job_titles_datasets(data_dir: str) -> Dict[str, Tuple[List[float], List[float]]]:
    """Load job title CSV files from the data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping job title names to (years, market_share) tuples
    """
    datasets = {}
    job_files = [
        ('job-title/analyst.csv', 'Analyst'),
        ('job-title/cyber-security.csv', 'Cyber Security'),
        ('job-title/data-analytics.csv', 'Data Analytics'),
        ('job-title/data-science.csv', 'Data Science'),
        ('job-title/devops.csv', 'Devops'),
        ('job-title/software-engineering.csv', 'Software Engineering'),
        ('job-title/web-development.csv', 'Web Development')
    ]
    
    for csv_file, display_name in job_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            datasets[display_name] = load_csv_data(file_path)
        else:
            print(f"Warning: {csv_file} not found at {file_path}")
            
    return datasets


def load_cloud_technology_datasets(data_dir: str) -> Dict[str, Tuple[List[float], List[float]]]:
    """Load cloud and technology CSV files from the data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping cloud/tech names to (years, market_share) tuples
    """
    datasets = {}
    cloud_tech_files = [
        # Cloud providers
        ('cloud/aws.csv', 'Aws'),
        ('cloud/azure.csv', 'Azure'),
        ('cloud/gcp.csv', 'Gcp'),
        # Technologies
        ('technology/docker.csv', 'Docker'),
        ('technology/kubernetes.csv', 'Kubernetes'),
        ('technology/terraform.csv', 'Terraform')
    ]
    
    for csv_file, display_name in cloud_tech_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            datasets[display_name] = load_csv_data(file_path)
        else:
            print(f"Warning: {csv_file} not found at {file_path}")
            
    return datasets


def load_themes_sectors_datasets(data_dir: str) -> Dict[str, Tuple[List[float], List[float]]]:
    """Load themes and sectors CSV files from the data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping theme/sector names to (years, market_share) tuples
    """
    datasets = {}
    themes_sectors_files = [
        # Themes
        ('themes/artificial-intelligence.csv', 'Artificial Intelligence'),
        ('themes/business-intelligence.csv', 'Business Intelligence'),
        ('themes/machine-learning.csv', 'Machine Learning'),
        ('themes/risk-management.csv', 'Risk Management'),
        # Sectors
        ('sectors/customer-service.csv', 'Customer Service'),
        ('sectors/finance.csv', 'Finance'),
        ('sectors/law.csv', 'Law'),
        ('sectors/marketing.csv', 'Marketing')
    ]
    
    for csv_file, display_name in themes_sectors_files:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            datasets[display_name] = load_csv_data(file_path)
        else:
            print(f"Warning: {csv_file} not found at {file_path}")
            
    return datasets