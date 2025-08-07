"""Generate comparison charts for each London Market Report section."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from job_board_parser import parse_job_board_csv
from comparison_chart_generator import create_comparison_chart
from itjobswatch_benchmarks import (
    PROGRAMMING_LANGUAGES, CLOUD_INFRASTRUCTURE, 
    JOB_TITLES, THEMES_SECTORS, THEMES_SECTORS_NO_FINANCE
)


def filter_data_by_categories(data, valid_categories):
    """Filter job board data to only include specified categories."""
    filtered = {}
    for board, keywords in data.items():
        filtered[board] = {}
        for keyword, count in keywords.items():
            keyword_lower = keyword.lower().strip()
            # Check if keyword matches any valid category
            for valid_cat in valid_categories:
                if keyword_lower == valid_cat.lower() or keyword_lower == valid_cat.lower().replace('#', 'sharp'):
                    filtered[board][keyword] = count
                    break
    return filtered


def main():
    """Generate all 5 report comparison charts."""
    # Setup paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'api' / 'data' / 'manual' / 'jobtitle_jobsboard_count.csv'
    output_dir = base_dir / 'reports' / 'jobs-boards'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse job board data
    print("Loading job board data...")
    raw_data = parse_job_board_csv(str(csv_path))
    
    # Report 1: Programming Languages
    print("\n=== Report 1: Programming Languages ===")
    lang_categories = list(PROGRAMMING_LANGUAGES.keys())
    lang_data = filter_data_by_categories(raw_data, lang_categories)
    
    create_comparison_chart(
        lang_data,
        PROGRAMMING_LANGUAGES,
        "Report 1: Programming Languages Market Comparison",
        str(output_dir / 'report1_languages_comparison.png')
    )
    
    # Report 2: Cloud & Infrastructure
    print("\n=== Report 2: Cloud & Technology Infrastructure ===")
    cloud_categories = list(CLOUD_INFRASTRUCTURE.keys())
    cloud_data = filter_data_by_categories(raw_data, cloud_categories)
    
    create_comparison_chart(
        cloud_data,
        CLOUD_INFRASTRUCTURE,
        "Report 2: Cloud & Infrastructure Market Comparison",
        str(output_dir / 'report2_cloud_comparison.png')
    )
    
    # Report 3: Job Titles
    print("\n=== Report 3: Job Titles ===")
    # Map job board keywords to ITJobsWatch categories - keeping software developer separate
    title_mapping = {
        'devops': 'devops',
        'software engineer': 'software engineer',
        'software developer': 'software developer',
        'data analyst': 'data analyst',
        'data scientist': 'data scientist',
        'web developer': 'web developer',
        'cyber security': 'cyber security'
    }
    
    # Create filtered data with proper mapping
    title_data = {}
    for board, keywords in raw_data.items():
        title_data[board] = {}
        for keyword, count in keywords.items():
            keyword_lower = keyword.lower().strip()
            if keyword_lower in title_mapping:
                mapped_key = title_mapping[keyword_lower]
                # Aggregate if already exists
                if mapped_key in title_data[board]:
                    title_data[board][mapped_key] += count
                else:
                    title_data[board][mapped_key] = count
    
    # Create ITJobsWatch data with unique keys - including software developer
    title_benchmarks = {
        'devops': 11.45,
        'software engineer': 8.35,
        'software developer': 0.59,  # Current ITJobsWatch market share
        'cyber security': 7.47,
        'data analyst': 2.58,  # Updated from CSV
        'data scientist': 3.74,  # Updated from CSV
        'web developer': 0.64  # Updated from CSV
    }
    
    # Debug output
    print("\nDEBUG: ITJobsWatch benchmarks being passed to chart:")
    for title, value in title_benchmarks.items():
        print(f"  {title}: {value}%")
    
    create_comparison_chart(
        title_data,
        title_benchmarks,
        "Report 3: Job Titles Market Comparison",
        str(output_dir / 'report3_titles_comparison.png')
    )
    
    print("\nAll 3 report comparison charts generated successfully!")
    print(f"Output directory: {output_dir}")
    
    # Print comparison summary
    print("\n=== COMPARISON SUMMARY ===")
    print("\nKey Observations:")
    print("1. Programming Languages: Python demand comparison across platforms vs ITJobsWatch 18.52%")
    print("2. Cloud Infrastructure: Azure (18.99%) vs AWS (15.69%) ITJobsWatch benchmarks")
    print("3. Job Titles: DevOps (11.45%) leads in ITJobsWatch market share")
    print("4. ITJobsWatch column synthesizes broader London market trends")
    print("5. Job boards show active hiring demand vs overall market presence")


if __name__ == "__main__":
    main()