"""Check ITJobsWatch benchmark values against CSV files."""

import os
from pathlib import Path

def get_latest_value(csv_path):
    """Get the most recent (last) value from a CSV file."""
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            # Filter out empty lines
            lines = [line.strip() for line in lines if line.strip()]
            if lines:
                last_line = lines[-1]
                if ',' in last_line:
                    parts = last_line.split(',')
                    if len(parts) >= 2:
                        return float(parts[1].strip())
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
    return None

# Base directory
base_dir = Path('api/data/manual/year_market-share')

# Categories to check
categories = {
    'Programming Languages': {
        'python': 'languages/python.csv',
        'java': 'languages/java.csv',
        'javascript': 'languages/javascript.csv',
        'typescript': 'languages/typescript.csv',
        'c#/csharp': 'languages/csharp.csv',
    },
    'Cloud & Infrastructure': {
        'azure': 'cloud/azure.csv',
        'aws': 'cloud/aws.csv',
        'kubernetes': 'technology/kubernetes.csv',
        'docker': 'technology/docker.csv',
        'terraform': 'technology/terraform.csv',
        'gcp': 'cloud/gcp.csv',
    },
    'Job Titles': {
        'analyst': 'job-title/analyst.csv',
        'devops': 'job-title/devops.csv',
        'software-engineering': 'job-title/software-engineering.csv',
        'cyber-security': 'job-title/cyber-security.csv',
        'data-analytics': 'job-title/data-analytics.csv',
        'data-science': 'job-title/data-science.csv',
        'web-development': 'job-title/web-development.csv',
        'software-developer': 'job-title/software-developer.csv',
    },
    'Themes & Sectors': {
        'finance': 'sectors/finance.csv',
        'artificial-intelligence': 'themes/artificial-intelligence.csv',
        'marketing': 'sectors/marketing.csv',
        'risk-management': 'themes/risk-management.csv',
        'machine-learning': 'themes/machine-learning.csv',
        'business-intelligence': 'themes/business-intelligence.csv',
        'customer-service': 'sectors/customer-service.csv',
        'law': 'sectors/law.csv',
    }
}

# Current benchmarks from code
current_benchmarks = {
    'Programming Languages': {
        'python': 18.52,
        'java': 8.02,
        'javascript': 7.21,
        'typescript': 5.79,
        'c#/csharp': 6.44,
    },
    'Cloud & Infrastructure': {
        'azure': 18.99,
        'aws': 15.69,
        'kubernetes': 6.25,
        'docker': 4.79,
        'terraform': 5.08,
        'gcp': 3.07,
    },
    'Job Titles': {
        'analyst': 10.51,
        'devops': 11.45,
        'software-engineering': 8.35,
        'cyber-security': 7.47,
        'data-analytics': 7.12,
        'data-science': 6.58,
        'web-development': 4.52,
        'software-developer': 0.59,
    },
    'Themes & Sectors': {
        'finance': 33.53,
        'artificial-intelligence': 11.46,
        'marketing': 8.45,
        'risk-management': 7.30,
        'machine-learning': 6.52,
        'business-intelligence': 5.85,
        'customer-service': 2.75,
        'law': 1.82,
    }
}

print("=" * 80)
print("ITJobsWatch Benchmark Comparison")
print("=" * 80)

for category_name, items in categories.items():
    print(f"\n{category_name}:")
    print("-" * 40)
    
    for key, csv_file in items.items():
        csv_path = base_dir / csv_file
        actual_value = get_latest_value(csv_path)
        current_value = current_benchmarks[category_name].get(key)
        
        if actual_value is not None:
            if current_value is not None:
                diff = abs(actual_value - current_value)
                status = "OK" if diff < 0.1 else "MISMATCH"
                print(f"  {key:30} Current: {current_value:6.2f}%  Actual: {actual_value:6.2f}%  {status}")
                if diff >= 0.1:
                    print(f"    -> NEEDS UPDATE: Change from {current_value:.2f}% to {actual_value:.2f}%")
            else:
                print(f"  {key:30} Not in benchmarks, CSV value: {actual_value:.2f}%")
        else:
            print(f"  {key:30} Could not read CSV file")

print("\n" + "=" * 80)
print("Summary of Required Updates:")
print("=" * 80)