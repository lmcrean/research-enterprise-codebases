"""Generate normalized (percentage-based) stacked bar charts for job board data."""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from job_board_parser import parse_job_board_csv, categorize_keywords, get_sorted_categories
from normalized_chart_generator import create_normalized_stacked_chart


def main():
    """Generate all three normalized job board stacked bar charts."""
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'api' / 'data' / 'manual' / 'jobtitle_jobsboard_count.csv'
    output_dir = base_dir / 'reports' / 'jobs-boards'
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Parse CSV data
    print(f"Loading data from: {csv_path}")
    raw_data = parse_job_board_csv(str(csv_path))
    
    # Print summary
    print("\nData Summary:")
    for board, keywords in raw_data.items():
        total_jobs = sum(keywords.values())
        print(f"{board}: {len(keywords)} keywords, {total_jobs} total jobs")
    
    # Categorize data
    print("\nCategorizing keywords...")
    all_data, job_titles_data, tech_lang_data = categorize_keywords(raw_data)
    
    # Get sorted categories for consistent ordering
    all_categories_sorted = get_sorted_categories(all_data)
    job_titles_sorted = get_sorted_categories(job_titles_data)
    tech_lang_sorted = get_sorted_categories(tech_lang_data)
    
    # Chart 1: All Categories Combined (Normalized)
    print("\nGenerating Normalized Chart 1: All Categories Combined")
    create_normalized_stacked_chart(
        all_data,
        "Job Board Demand Analysis - All Categories (% of Total)",
        str(output_dir / 'all_categories_normalized.png'),
        categories_order=all_categories_sorted
    )
    
    # Chart 2: Job Titles Only (Normalized)
    print("\nGenerating Normalized Chart 2: Job Titles Only")
    create_normalized_stacked_chart(
        job_titles_data,
        "Job Board Demand Analysis - Job Titles (% of Total)",
        str(output_dir / 'job_titles_normalized.png'),
        categories_order=job_titles_sorted
    )
    
    # Chart 3: Technologies & Languages (Normalized)
    print("\nGenerating Normalized Chart 3: Technologies & Languages")
    create_normalized_stacked_chart(
        tech_lang_data,
        "Job Board Demand Analysis - Technologies & Languages (% of Total)",
        str(output_dir / 'technologies_languages_normalized.png'),
        categories_order=tech_lang_sorted
    )
    
    print("\nAll normalized charts generated successfully!")
    
    # Print demand analysis
    print("\n=== DEMAND ANALYSIS ===")
    
    print("\nTop 5 In-Demand Categories (All):")
    for cat in all_categories_sorted[:5]:
        total = sum(all_data[board].get(cat, 0) for board in all_data.keys())
        percentages = []
        for board in all_data.keys():
            board_total = sum(all_data[board].values())
            if board_total > 0:
                pct = (all_data[board].get(cat, 0) / board_total) * 100
                percentages.append(f"{board}: {pct:.1f}%")
        print(f"  {cat}: {total} total jobs")
        print(f"    Distribution: {', '.join(percentages)}")
    
    print("\nTop 5 In-Demand Job Titles:")
    for cat in job_titles_sorted[:5]:
        total = sum(job_titles_data[board].get(cat, 0) for board in job_titles_data.keys())
        print(f"  {cat}: {total} total jobs")
    
    print("\nTop 5 In-Demand Technologies & Languages:")
    for cat in tech_lang_sorted[:5]:
        total = sum(tech_lang_data[board].get(cat, 0) for board in tech_lang_data.keys())
        print(f"  {cat}: {total} total jobs")


if __name__ == "__main__":
    main()