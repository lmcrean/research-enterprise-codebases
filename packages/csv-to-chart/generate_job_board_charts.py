"""Generate stacked bar charts for job board data."""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from job_board_parser import parse_job_board_csv, categorize_keywords, get_sorted_categories
from stacked_chart_generator import create_stacked_bar_chart


def main():
    """Generate all three job board stacked bar charts."""
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'api' / 'data' / 'manual' / 'jobtitle_jobsboard_count.csv'
    output_dir = base_dir / 'reports' / 'jobs-boards'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Parse CSV data
    print(f"Loading data from: {csv_path}")
    raw_data = parse_job_board_csv(str(csv_path))
    
    # Print summary
    for board, keywords in raw_data.items():
        print(f"{board}: {len(keywords)} keywords, {sum(keywords.values())} total jobs")
    
    # Categorize data
    print("\nCategorizing keywords...")
    all_data, job_titles_data, tech_lang_data = categorize_keywords(raw_data)
    
    # Get sorted categories for consistent ordering
    all_categories_sorted = get_sorted_categories(all_data)
    job_titles_sorted = get_sorted_categories(job_titles_data)
    tech_lang_sorted = get_sorted_categories(tech_lang_data)
    
    # Chart 1: All Categories Combined
    print("\nGenerating Chart 1: All Categories Combined")
    create_stacked_bar_chart(
        all_data,
        "Job Board Comparison - All Categories",
        str(output_dir / 'all_categories_stacked.png'),
        categories_order=all_categories_sorted
    )
    
    # Chart 2: Job Titles Only
    print("\nGenerating Chart 2: Job Titles Only")
    create_stacked_bar_chart(
        job_titles_data,
        "Job Board Comparison - Job Titles",
        str(output_dir / 'job_titles_stacked.png'),
        categories_order=job_titles_sorted
    )
    
    # Chart 3: Technologies & Languages
    print("\nGenerating Chart 3: Technologies & Languages")
    create_stacked_bar_chart(
        tech_lang_data,
        "Job Board Comparison - Technologies & Languages",
        str(output_dir / 'technologies_languages_stacked.png'),
        categories_order=tech_lang_sorted
    )
    
    print("\nAll charts generated successfully!")
    print(f"Output directory: {output_dir}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("\nAll Categories:")
    for cat in all_categories_sorted[:5]:
        total = sum(all_data[board].get(cat, 0) for board in all_data.keys())
        print(f"  {cat}: {total} total jobs")
    
    print("\nTop Job Titles:")
    for cat in job_titles_sorted[:5]:
        total = sum(job_titles_data[board].get(cat, 0) for board in job_titles_data.keys())
        print(f"  {cat}: {total} total jobs")
    
    print("\nTop Technologies & Languages:")
    for cat in tech_lang_sorted[:5]:
        total = sum(tech_lang_data[board].get(cat, 0) for board in tech_lang_data.keys())
        print(f"  {cat}: {total} total jobs")


if __name__ == "__main__":
    main()