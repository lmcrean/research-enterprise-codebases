"""Data models for ITJobsWatch historical trend data."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class TrendDataPoint:
    """Single data point in a trend timeline."""
    year: int
    value: float
    month: Optional[int] = None
    data_type: str = "job_count"  # job_count, market_percentage, median_salary
    total_market_jobs: Optional[int] = None  # Total IT jobs for percentage calculation
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'year': self.year,
            'month': self.month,
            'value': self.value,
            'type': self.data_type,
            'total_market_jobs': self.total_market_jobs
        }
    
    def calculate_market_percentage(self, total_jobs: int) -> float:
        """Calculate market share percentage given total market size."""
        if total_jobs <= 0:
            return 0.0
        return (self.value / total_jobs) * 100


@dataclass
class TechnologyTrend:
    """Historical trend data for a specific technology."""
    technology: str
    data_points: List[TrendDataPoint] = field(default_factory=list)
    url: Optional[str] = None
    last_updated: Optional[str] = None
    
    def add_data_point(self, year: int, value: float, data_type: str = "job_count", month: Optional[int] = None, total_market_jobs: Optional[int] = None):
        """Add a new data point to the trend."""
        self.data_points.append(TrendDataPoint(year, value, month, data_type, total_market_jobs))
    
    def get_data_by_type(self, data_type: str) -> List[TrendDataPoint]:
        """Get all data points of a specific type."""
        return [dp for dp in self.data_points if dp.data_type == data_type]
    
    def get_years_range(self) -> tuple:
        """Get the min and max years in the data."""
        if not self.data_points:
            return (None, None)
        years = [dp.year for dp in self.data_points]
        return (min(years), max(years))
    
    def generate_market_percentage_data(self, total_jobs_by_year: Dict[int, int]):
        """Generate market percentage data points from job count data."""
        job_count_points = self.get_data_by_type("job_count")
        
        for point in job_count_points:
            if point.year in total_jobs_by_year:
                total_jobs = total_jobs_by_year[point.year]
                percentage = point.calculate_market_percentage(total_jobs)
                
                # Add percentage data point
                self.add_data_point(
                    year=point.year,
                    value=percentage,
                    data_type="market_percentage",
                    month=point.month,
                    total_market_jobs=total_jobs
                )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'technology': self.technology,
            'url': self.url,
            'last_updated': self.last_updated,
            'data_points': [dp.to_dict() for dp in self.data_points]
        }


@dataclass
class TrendCollection:
    """Collection of technology trends."""
    trends: Dict[str, TechnologyTrend] = field(default_factory=dict)
    collection_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    
    def add_technology(self, technology: str, url: Optional[str] = None) -> TechnologyTrend:
        """Add a new technology to track."""
        if technology not in self.trends:
            self.trends[technology] = TechnologyTrend(
                technology=technology,
                url=url,
                last_updated=self.collection_date
            )
        return self.trends[technology]
    
    def get_technology(self, technology: str) -> Optional[TechnologyTrend]:
        """Get trend data for a specific technology."""
        return self.trends.get(technology)
    
    def get_all_technologies(self) -> List[str]:
        """Get list of all tracked technologies."""
        return list(self.trends.keys())
    
    def to_dataframe_format(self) -> List[Dict]:
        """Convert to format suitable for pandas DataFrame."""
        rows = []
        for tech_name, tech_trend in self.trends.items():
            for dp in tech_trend.data_points:
                rows.append({
                    'Technology': tech_name,
                    'Year': dp.year,
                    'Month': dp.month,
                    'Value': dp.value,
                    'Type': dp.data_type,
                    'URL': tech_trend.url,
                    'Total_Market_Jobs': dp.total_market_jobs
                })
        return rows