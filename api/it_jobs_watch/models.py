"""Data models for IT Jobs Watch market statistics."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class JobMarketStats:
    """Job market statistics from IT Jobs Watch."""
    technology: str
    demand_rank: int
    rank_change: int
    median_salary: int
    salary_change: str
    total_vacancies: int
    live_jobs: int
    location: str
    collected_at: str

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'Technology': self.technology,
            'Demand Rank': self.demand_rank,
            'Rank Change': self.rank_change,
            'Median Salary': self.median_salary,
            'Salary Change': self.salary_change,
            'Total Vacancies': self.total_vacancies,
            'Live Jobs': self.live_jobs,
            'Location': self.location,
            'Collected At': self.collected_at
        }


@dataclass
class JobMarketMetadata:
    """Metadata about job market data collection run."""
    last_updated: str
    total_technologies: int
    location: str
    collection_time_seconds: float
    
    @classmethod
    def create(cls, tech_count: int, location: str, collection_time: float) -> 'JobMarketMetadata':
        """Create metadata with current timestamp."""
        return cls(
            last_updated=datetime.now().isoformat(),
            total_technologies=tech_count,
            location=location,
            collection_time_seconds=round(collection_time, 2)
        )