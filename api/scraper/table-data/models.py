"""
Data models for ITJobsWatch table data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class JobListing:
    """Represents a single job listing from IT Jobs Watch."""
    
    skill_name: str
    rank: int
    rank_change: Optional[int]
    rank_change_direction: Optional[str]  # '+', '-', or None
    median_salary: Optional[int]
    salary_change_percentage: Optional[float]
    historical_vacancies_count: Optional[int]
    historical_vacancies_percentage: Optional[float]
    live_jobs_count: int
    location: str
    scrape_date: datetime
    
    @classmethod
    def from_row_data(cls, row_data: dict, location: str) -> 'JobListing':
        """
        Create JobListing from parsed row data.
        
        Args:
            row_data: Dictionary containing parsed row data
            location: Location for this listing
        
        Returns:
            JobListing instance
        """
        # Parse rank change - preserve signed integer
        rank_change = None
        rank_change_direction = None
        if row_data.get('rank_change'):
            change_str = row_data['rank_change']
            if change_str not in ['0', '-']:
                if change_str.startswith('+'):
                    rank_change_direction = '+'
                    rank_change = int(change_str[1:])
                elif change_str.startswith('-'):
                    rank_change_direction = '-'
                    rank_change = -int(change_str[1:])  # Keep negative value
                else:
                    # Handle cases where it's just a number
                    try:
                        rank_change = int(change_str)
                        rank_change_direction = '+' if rank_change > 0 else ('-' if rank_change < 0 else '')
                    except ValueError:
                        pass
        
        # Parse median salary (remove £ and commas)
        median_salary = None
        if row_data.get('median_salary'):
            salary_str = row_data['median_salary'].replace('£', '').replace(',', '')
            if salary_str and salary_str != '-':
                median_salary = int(salary_str)
        
        # Parse salary change percentage
        salary_change = None
        if row_data.get('salary_change'):
            change_str = row_data['salary_change']
            if change_str and change_str != '-':
                # Remove % and parse
                change_str = change_str.replace('%', '')
                if change_str.startswith('+'):
                    salary_change = float(change_str[1:])
                elif change_str.startswith('-'):
                    salary_change = -float(change_str[1:])
        
        # Parse historical vacancies (format: "1,234 12.34%")
        hist_count = None
        hist_percentage = None
        if row_data.get('historical_vacancies'):
            hist_str = row_data['historical_vacancies']
            parts = hist_str.split()
            if parts:
                # Parse count
                count_str = parts[0].replace(',', '')
                if count_str.isdigit():
                    hist_count = int(count_str)
                
                # Parse percentage
                if len(parts) > 1:
                    pct_str = parts[1].replace('%', '')
                    try:
                        hist_percentage = float(pct_str)
                    except ValueError:
                        pass
        
        # Parse live jobs count
        live_jobs = 0
        if row_data.get('live_jobs'):
            jobs_str = row_data['live_jobs'].replace(',', '')
            if jobs_str.isdigit():
                live_jobs = int(jobs_str)
        
        return cls(
            skill_name=row_data['skill_name'],
            rank=int(row_data['rank']),
            rank_change=rank_change,
            rank_change_direction=rank_change_direction,
            median_salary=median_salary,
            salary_change_percentage=salary_change,
            historical_vacancies_count=hist_count,
            historical_vacancies_percentage=hist_percentage,
            live_jobs_count=live_jobs,
            location=location,
            scrape_date=datetime.now()
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export."""
        return {
            'skill_name': self.skill_name,
            'rank': self.rank,
            'rank_change': self.rank_change if self.rank_change else 0,
            'rank_change_direction': self.rank_change_direction or '',
            'median_salary': self.median_salary or '',
            'salary_change_percentage': self.salary_change_percentage if self.salary_change_percentage is not None else '',
            'historical_vacancies_count': self.historical_vacancies_count or '',
            'historical_vacancies_percentage': self.historical_vacancies_percentage if self.historical_vacancies_percentage is not None else '',
            'live_jobs_count': self.live_jobs_count,
            'location': self.location,
            'scrape_date': self.scrape_date.isoformat()
        }


@dataclass
class ScrapeMetadata:
    """Metadata about a scraping session."""
    
    location: str
    total_records: int
    total_pages: int
    scrape_start: datetime
    scrape_end: datetime
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            'location': self.location,
            'total_records': self.total_records,
            'total_pages': self.total_pages,
            'scrape_start': self.scrape_start.isoformat(),
            'scrape_end': self.scrape_end.isoformat(),
            'success': self.success,
            'error_message': self.error_message,
            'duration_seconds': (self.scrape_end - self.scrape_start).total_seconds()
        }