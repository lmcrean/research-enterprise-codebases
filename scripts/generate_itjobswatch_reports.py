"""Generate markdown reports from IT Jobs Watch data."""

import os
import sys
import pandas as pd
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.github.utils import format_number


def load_itjobswatch_data():
    """Load IT Jobs Watch data from CSV and metadata from JSON."""
    data_dir = "data/raw"
    csv_path = os.path.join(data_dir, "itjobswatch_stats.csv")
    metadata_path = os.path.join(data_dir, "itjobswatch_metadata.json")
    
    if not os.path.exists(csv_path):
        print(f"❌ Data file not found: {csv_path}")
        return None, None
    
    # Load CSV data
    df = pd.read_csv(csv_path)
    
    # Load metadata
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    
    return df, metadata


def generate_summary_report(df, metadata):
    """Generate summary report of all job market data."""
    
    # Calculate summary statistics
    total_roles = len(df)
    avg_salary = df[df['Median Salary'] > 0]['Median Salary'].mean()
    total_vacancies = df['Total Vacancies'].sum()
    total_live_jobs = df['Live Jobs'].sum()
    
    # Top technologies by demand rank
    top_by_rank = df[df['Demand Rank'] > 0].nsmallest(10, 'Demand Rank')
    
    # Top technologies by salary
    top_by_salary = df[df['Median Salary'] > 0].nlargest(10, 'Median Salary')
    
    # Generate report
    report = f"""# London IT Job Market Analysis

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Summary Statistics

- **Total Job Roles Analyzed**: {total_roles:,}
- **Average Median Salary**: £{avg_salary:,.0f}
- **Total Job Vacancies**: {format_number(total_vacancies)}
- **Current Live Jobs**: {format_number(total_live_jobs)}
- **Data Collection Time**: {metadata.get('collection_time_seconds', 'N/A')} seconds

## Top Technologies by Demand Ranking

| Technology | Demand Rank | Median Salary | Total Vacancies | Live Jobs | Rank Change |
|------------|-------------|---------------|-----------------|-----------|-------------|
"""
    
    for _, row in top_by_rank.iterrows():
        salary_str = f"£{row['Median Salary']:,}" if row['Median Salary'] > 0 else "N/A"
        change_str = f"+{row['Rank Change']}" if row['Rank Change'] > 0 else str(row['Rank Change'])
        if row['Rank Change'] == 0:
            change_str = "-"
        
        report += f"| [{row['Technology']}](https://www.itjobswatch.co.uk/default.aspx?q={row['Technology'].replace(' ', '%20')}) | {row['Demand Rank']} | {salary_str} | {format_number(row['Total Vacancies'])} | {format_number(row['Live Jobs'])} | {change_str} |\n"
    
    report += f"""

## Highest Paying Technologies

| Technology | Median Salary | Demand Rank | Total Vacancies | Live Jobs |
|------------|---------------|-------------|-----------------|-----------|
"""
    
    for _, row in top_by_salary.iterrows():
        rank_str = str(row['Demand Rank']) if row['Demand Rank'] > 0 else "N/A"
        
        report += f"| [{row['Technology']}](https://www.itjobswatch.co.uk/default.aspx?q={row['Technology'].replace(' ', '%20')}) | £{row['Median Salary']:,} | {rank_str} | {format_number(row['Total Vacancies'])} | {format_number(row['Live Jobs'])} |\n"
    
    # Technology categories analysis
    report += """

## Key Technology Categories

### Programming Languages
"""
    
    languages = df[df['Technology'].str.contains('Python|C#|TypeScript|JavaScript|Java', case=False, na=False)]
    if not languages.empty:
        for _, row in languages.iterrows():
            salary_str = f"£{row['Median Salary']:,}" if row['Median Salary'] > 0 else "N/A"
            report += f"- **{row['Technology']}**: Rank #{row['Demand Rank']}, {salary_str} median salary, {format_number(row['Live Jobs'])} live jobs\n"
    
    report += """
### Emerging Technologies
"""
    
    emerging = df[df['Technology'].str.contains('AI|Artificial Intelligence|Machine Learning|Data Science', case=False, na=False)]
    if not emerging.empty:
        for _, row in emerging.iterrows():
            salary_str = f"£{row['Median Salary']:,}" if row['Median Salary'] > 0 else "N/A"
            report += f"- **{row['Technology']}**: Rank #{row['Demand Rank']}, {salary_str} median salary, {format_number(row['Live Jobs'])} live jobs\n"
    
    report += f"""

---
*Data collected from [ITJobsWatch](https://www.itjobswatch.co.uk) on {metadata.get('last_updated', 'Unknown')}*
*London market analysis for {len(df['Technology'].unique())} unique job roles*
"""
    
    return report


def generate_technology_reports(df):
    """Generate individual reports for key technology categories."""
    
    categories = {
        'python': {
            'name': 'Python Development',
            'filter': lambda x: 'python' in x.lower(),
            'description': 'Python development roles including Django, Flask, and data science positions'
        },
        'csharp': {
            'name': 'C# Development', 
            'filter': lambda x: 'c#' in x.lower() or '.net' in x.lower(),
            'description': 'C# and .NET development opportunities in London'
        },
        'typescript': {
            'name': 'TypeScript Development',
            'filter': lambda x: 'typescript' in x.lower() or 'angular' in x.lower() or 'react' in x.lower() or 'node' in x.lower(),
            'description': 'TypeScript, Angular, React, and Node.js development roles'
        },
        'ai_ml': {
            'name': 'AI & Machine Learning',
            'filter': lambda x: any(term in x.lower() for term in ['ai', 'artificial intelligence', 'machine learning', 'data scien']),
            'description': 'Artificial Intelligence and Machine Learning career opportunities'
        }
    }
    
    reports = {}
    
    for key, category in categories.items():
        category_df = df[df['Technology'].apply(category['filter'])]
        
        if category_df.empty:
            continue
        
        # Sort by demand rank
        category_df = category_df.sort_values('Demand Rank')
        
        avg_salary = category_df[category_df['Median Salary'] > 0]['Median Salary'].mean()
        total_jobs = category_df['Live Jobs'].sum()
        
        report = f"""# {category['name']} - London Job Market

*{category['description']}*

## Market Overview

- **Total Job Roles**: {len(category_df)}
- **Average Salary**: £{avg_salary:,.0f}
- **Total Live Jobs**: {format_number(total_jobs)}

## Detailed Job Roles

| Role | Demand Rank | Median Salary | Live Jobs | Total Vacancies | YoY Change |
|------|-------------|---------------|-----------|-----------------|------------|
"""
        
        for _, row in category_df.iterrows():
            salary_str = f"£{row['Median Salary']:,}" if row['Median Salary'] > 0 else "N/A"
            rank_str = str(row['Demand Rank']) if row['Demand Rank'] > 0 else "N/A"
            
            report += f"| [{row['Technology']}](https://www.itjobswatch.co.uk/default.aspx?q={row['Technology'].replace(' ', '%20')}) | {rank_str} | {salary_str} | {format_number(row['Live Jobs'])} | {format_number(row['Total Vacancies'])} | {row['Salary Change']} |\n"
        
        report += """

---
*Data sourced from ITJobsWatch for London market analysis*
"""
        
        reports[key] = report
    
    return reports


def main():
    """Generate all IT Jobs Watch reports."""
    print("📊 Generating IT Jobs Watch reports...")
    
    # Load data
    df, metadata = load_itjobswatch_data()
    if df is None:
        return
    
    # Ensure views directory exists
    views_dir = "views"
    os.makedirs(views_dir, exist_ok=True)
    
    # Generate summary report
    summary_report = generate_summary_report(df, metadata)
    summary_path = os.path.join(views_dir, "itjobswatch_summary.md")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_report)
    print(f"✅ Generated summary report: {summary_path}")
    
    # Generate technology category reports
    tech_reports = generate_technology_reports(df)
    
    for category, report in tech_reports.items():
        report_path = os.path.join(views_dir, f"itjobswatch_{category}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Generated {category} report: {report_path}")
    
    print(f"🎉 Report generation complete! Generated {1 + len(tech_reports)} reports")


if __name__ == "__main__":
    main()