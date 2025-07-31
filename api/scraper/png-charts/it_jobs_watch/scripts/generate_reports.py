"""Generate markdown reports from ITJobsWatch market data."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import os

class ITJobsWatchReportGenerator:
    """Generates markdown reports from ITJobsWatch market data."""
    
    def __init__(self, data_path: str = 'data/scraped/itjobswatch'):
        """Initialize with path to ITJobsWatch data."""
        self.data_path = Path(data_path)
        self.file_data_path = self.data_path / 'file-data'
        self.table_data_path = self.data_path / 'table-data'
        
    def generate_all_reports(self):
        """Generate all markdown reports."""
        print("Generating ITJobsWatch market reports...")
        
        self.generate_market_overview_report()
        self.generate_technology_reports()
        self.generate_job_trends_report()
        
        print("All ITJobsWatch reports generated successfully!")
    
    def generate_market_overview_report(self):
        """Generate comprehensive market overview report."""
        # Load available technology data
        tech_files = list(self.file_data_path.glob('*.json')) if self.file_data_path.exists() else []
        tech_data = {}
        
        for tech_file in tech_files:
            tech_name = tech_file.stem
            try:
                with open(tech_file, 'r') as f:
                    tech_data[tech_name] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {tech_file}: {e}")
        
        # Build markdown content
        content = f"""# ITJobsWatch Market Analysis - Overview

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Summary

This report analyzes UK job market trends based on data scraped from ITJobsWatch, focusing on technology demand and market dynamics.

## Available Technologies

"""
        
        if tech_data:
            content += f"- **Total Technologies Tracked**: {len(tech_data)}\n\n"
            for tech_name in sorted(tech_data.keys()):
                formatted_name = tech_name.replace('-', ' ').title()
                content += f"- **{formatted_name}**\n"
        else:
            content += "No technology data available yet.\n\n"
        
        # Add table data summary if available
        if self.table_data_path.exists():
            table_files = list(self.table_data_path.glob('*.csv'))
            if table_files:
                content += f"""
## Job Market Data

- **Job Listing Files**: {len(table_files)}
"""
                for table_file in table_files:
                    try:
                        df = pd.read_csv(table_file)
                        content += f"- **{table_file.stem}**: {len(df)} job listings\n"
                    except Exception as e:
                        content += f"- **{table_file.stem}**: Error loading data\n"
        
        content += f"""

## Data Sources

### Chart Data (PNG Analysis)
- Source: ITJobsWatch trend charts
- Analysis: Computer vision and OCR extraction
- Focus: Market share and growth trends over time

### Table Data (Job Listings)
- Source: ITJobsWatch job listings
- Analysis: Direct web scraping
- Focus: Current job availability and salary ranges

## Report Categories

- [Market Growth Trends](market-reports/growth-markets.md)
- [Technology Comparison](report.md)

---
*Generated automatically from ITJobsWatch data*
"""
        
        # Ensure docs directory exists
        os.makedirs('docs', exist_ok=True)
        
        # Write to file
        with open('docs/all.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Generated docs/all.md")
    
    def generate_technology_reports(self):
        """Generate individual technology reports."""
        if not self.file_data_path.exists():
            print("No technology data directory found")
            return
            
        tech_files = list(self.file_data_path.glob('*.json'))
        
        for tech_file in tech_files:
            tech_name = tech_file.stem
            try:
                with open(tech_file, 'r') as f:
                    tech_data = json.load(f)
                self._generate_technology_report(tech_name, tech_data)
            except Exception as e:
                print(f"Warning: Could not generate report for {tech_name}: {e}")
    
    def _generate_technology_report(self, tech_name: str, tech_data: Dict):
        """Generate report for specific technology."""
        formatted_name = tech_name.replace('-', ' ').title()
        
        content = f"""# {formatted_name} Market Analysis

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Technology: {formatted_name}

### Data Overview
- **Data Source**: ITJobsWatch
- **Analysis Type**: Market trend extraction from charts
- **Technology**: {formatted_name}

### Available Data
"""
        
        # Add data summary based on what's available
        if isinstance(tech_data, dict):
            if 'metadata' in tech_data:
                content += f"- **Data Collection**: {tech_data['metadata'].get('timestamp', 'Unknown')}\n"
            if 'chart_data' in tech_data:
                content += f"- **Chart Data Points**: {len(tech_data['chart_data'])}\n"
        
        content += f"""

### Market Insights

*Analysis based on ITJobsWatch trend data for {formatted_name}*

### Chart Analysis
- Chart data has been extracted using computer vision techniques
- Trend analysis shows market demand patterns over time
- Data points represent relative market share and growth

---
[← Back to Overview](all.md)

*Generated automatically from ITJobsWatch data*
"""
        
        # Ensure docs directory exists
        os.makedirs('docs', exist_ok=True)
        
        # Write to file
        filename = f'docs/{tech_name.replace(" ", "_").lower()}.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Generated {filename}")
    
    def generate_job_trends_report(self):
        """Generate job trends report from table data."""
        if not self.table_data_path.exists():
            print("No table data directory found")
            return
        
        content = f"""# Job Market Trends Analysis

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Job Listing Analysis

This report analyzes current job market trends based on scraped job listing data from ITJobsWatch.

"""
        
        # Analyze table data files
        table_files = list(self.table_data_path.glob('*.csv'))
        
        if table_files:
            content += f"### Available Data\n\n"
            total_jobs = 0
            
            for table_file in table_files:
                try:
                    df = pd.read_csv(table_file)
                    job_count = len(df)
                    total_jobs += job_count
                    
                    content += f"- **{table_file.stem}**: {job_count:,} job listings\n"
                    
                    # Add basic statistics if salary data exists
                    if 'salary' in df.columns or 'Salary' in df.columns:
                        salary_col = 'salary' if 'salary' in df.columns else 'Salary'
                        # Basic salary analysis would go here
                        content += f"  - Salary data available\n"
                    
                except Exception as e:
                    content += f"- **{table_file.stem}**: Error loading data ({e})\n"
            
            content += f"\n**Total Job Listings**: {total_jobs:,}\n\n"
        else:
            content += "No job listing data available yet.\n\n"
        
        content += f"""
### Analysis Notes

- Data extracted from ITJobsWatch job listings
- Represents current UK job market snapshot
- Includes location, salary, and technology focus areas

---
[← Back to Overview](all.md)

*Generated automatically from ITJobsWatch data*
"""
        
        # Ensure docs directory exists
        os.makedirs('docs', exist_ok=True)
        
        # Write to file
        with open('docs/job_trends.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Generated docs/job_trends.md")


def main():
    """Main report generation function."""
    generator = ITJobsWatchReportGenerator()
    generator.generate_all_reports()


if __name__ == '__main__':
    main()