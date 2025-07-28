"""Generate markdown reports from collected GitHub data."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add api package to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from api.github.utils import format_repo_stats_for_display


class ReportGenerator:
    """Generates markdown reports from GitHub data."""
    
    def __init__(self, data_path: str = 'data/raw/github_repository_stats.csv'):
        """Initialize with path to CSV data."""
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load collection metadata."""
        metadata_path = Path(self.data_path).parent / 'github_stats_metadata.json'
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def generate_all_reports(self):
        """Generate all markdown reports."""
        print("Generating markdown reports...")
        
        self.generate_overview_report()
        self.generate_category_reports()
        
        print("All reports generated successfully!")
    
    def generate_overview_report(self):
        """Generate comprehensive overview report."""
        # Get summary statistics
        total_repos = len(self.df)
        total_stars = self.df['Stars'].sum()
        categories = self.df['Field'].unique()
        
        # Get top repositories
        top_repos = self.df.nlargest(10, 'Stars')
        top_repos_formatted = format_repo_stats_for_display(top_repos.to_dict('records'))
        
        # Build markdown content
        content = f"""# Enterprise Codebases Research - Overview

*Last updated: {self.metadata.get('last_updated', 'Unknown')}*

## Summary Statistics

- **Total Repositories**: {total_repos:,}
- **Total Stars**: {total_stars:,}
- **Technology Categories**: {len(categories)}
- **Collection Time**: {self.metadata.get('collection_time_seconds', 0):.1f} seconds

## Technology Categories

"""
        
        # Add category breakdown
        for category in sorted(categories):
            category_df = self.df[self.df['Field'] == category]
            category_stars = category_df['Stars'].sum()
            content += f"- **{category}**: {len(category_df)} repositories ({category_stars:,} total stars)\n"
        
        content += f"""
## Top 10 Most Starred Repositories

| Repository | Category | Stars | Forks | Contributors | Open PRs |
|------------|----------|-------|-------|--------------|----------|
"""
        
        for repo in top_repos_formatted:
            content += f"| [{repo['Name']}](https://github.com/{repo['Name']}) | {repo['Field']} | {repo['Stars']} | {repo['Forks']} | {repo['Contributors']} | {repo['Open Pull Requests']} |\n"
        
        content += f"""
## Category Reports

- [AI/ML Repositories](ai_ml.md)
- [TypeScript Repositories](typescript.md)  
- [C# ASP.NET Repositories](csharp.md)
- [Developer Tools](developer_tools.md)

---
*Generated automatically from GitHub API data*
"""
        
        # Write to file
        with open('views/all.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Generated views/all.md")
    
    def generate_category_reports(self):
        """Generate individual category reports."""
        categories = {
            'AI/ML': 'ai_ml.md',
            'TypeScript': 'typescript.md', 
            'C# ASP.NET': 'csharp.md',
            'Developer_Tools': 'developer_tools.md'
        }
        
        for category, filename in categories.items():
            self._generate_category_report(category, filename)
    
    def _generate_category_report(self, category: str, filename: str):
        """Generate report for specific category."""
        category_df = self.df[self.df['Field'] == category].copy()
        
        if category_df.empty:
            print(f"Warning: No data found for category: {category}")
            return
        
        # Sort by stars descending
        category_df = category_df.sort_values('Stars', ascending=False)
        category_repos = format_repo_stats_for_display(category_df.to_dict('records'))
        
        # Calculate statistics
        total_repos = len(category_df)
        total_stars = category_df['Stars'].sum()
        avg_stars = category_df['Stars'].mean()
        
        # Build content
        content = f"""# {category} Repositories

*Last updated: {self.metadata.get('last_updated', 'Unknown')}*

## Overview

- **Total Repositories**: {total_repos}
- **Total Stars**: {total_stars:,}
- **Average Stars**: {avg_stars:,.0f}

## Repository Details

| Repository | Stars | Forks | Contributors | Open Issues | Open PRs | Created | Last Active |
|------------|-------|-------|--------------|-------------|----------|---------|-------------|
"""
        
        for repo in category_repos:
            content += f"| [{repo['Name']}](https://github.com/{repo['Name']}) | {repo['Stars']} | {repo['Forks']} | {repo['Contributors']} | {repo['Open Issues']} | {repo['Open Pull Requests']} | {repo['Date Created']} | {repo['Last Active']} |\n"
        
        content += f"""
## Key Insights

### Most Popular
- **{category_repos[0]['Name']}**: {category_repos[0]['Stars']} stars

### Most Active Development
"""
        
        # Find most active (recent pushes + high PR count)
        recent_active = category_df.nlargest(3, 'Open Pull Requests')
        for _, repo in recent_active.iterrows():
            repo_formatted = format_repo_stats_for_display([repo.to_dict()])[0]
            content += f"- **{repo_formatted['Name']}**: {repo_formatted['Open Pull Requests']} open PRs\n"
        
        content += f"""
---
[← Back to Overview](all.md)

*Generated automatically from GitHub API data*
"""
        
        # Write to file
        filepath = f'views/{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Generated {filepath}")


def main():
    """Main report generation function."""
    generator = ReportGenerator()
    generator.generate_all_reports()


if __name__ == '__main__':
    main()