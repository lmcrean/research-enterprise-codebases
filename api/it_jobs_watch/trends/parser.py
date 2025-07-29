"""Parser for extracting trend data from ITJobsWatch chart data."""

import re
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime

try:
    from .models import TrendDataPoint
except ImportError:
    from models import TrendDataPoint


class TrendParser:
    """Parses JavaScript chart data and HTML tables to extract trend information."""
    
    def parse_chart_data(self, chart_data: Dict[str, str]) -> List[TrendDataPoint]:
        """Parse chart data dictionary into TrendDataPoint objects."""
        data_points = []
        
        # Parse categories (dates/years)
        categories = self._parse_categories(chart_data.get('categories', ''))
        
        # Parse job vacancy data
        if 'jobs' in chart_data:
            job_values = self._parse_data_array(chart_data['jobs'])
            for i, (year, month) in enumerate(categories):
                if i < len(job_values):
                    data_points.append(
                        TrendDataPoint(year, job_values[i], month, 'job_count')
                    )
        
        # Parse salary data
        if 'salary' in chart_data:
            salary_values = self._parse_data_array(chart_data['salary'])
            for i, (year, month) in enumerate(categories):
                if i < len(salary_values):
                    data_points.append(
                        TrendDataPoint(year, salary_values[i], month, 'median_salary')
                    )
        
        return data_points
    
    def _parse_categories(self, categories_str: str) -> List[Tuple[int, Optional[int]]]:
        """Parse categories string to extract years and optional months."""
        categories = []
        
        # Remove quotes and split by comma
        items = re.findall(r'["\']([^"\']+)["\']', categories_str)
        
        for item in items:
            # Try to parse different date formats
            year, month = self._parse_date_string(item)
            if year:
                categories.append((year, month))
        
        return categories
    
    def _parse_date_string(self, date_str: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse various date string formats."""
        # Try year only (e.g., "2023")
        if re.match(r'^\d{4}$', date_str):
            return int(date_str), None
        
        # Try month-year format (e.g., "Jan 2023", "01/2023")
        month_year_match = re.match(r'(\w+)\s+(\d{4})', date_str)
        if month_year_match:
            month_str, year = month_year_match.groups()
            month = self._month_to_number(month_str)
            return int(year), month
        
        # Try numeric month/year (e.g., "01/2023")
        numeric_match = re.match(r'(\d{1,2})/(\d{4})', date_str)
        if numeric_match:
            month, year = numeric_match.groups()
            return int(year), int(month)
        
        return None, None
    
    def _month_to_number(self, month_str: str) -> Optional[int]:
        """Convert month name to number."""
        months = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        return months.get(month_str.lower())
    
    def _parse_data_array(self, data_str: str) -> List[float]:
        """Parse JavaScript array of numbers."""
        values = []
        
        # Extract numbers from the string
        numbers = re.findall(r'-?\d+\.?\d*', data_str)
        
        for num in numbers:
            try:
                values.append(float(num))
            except ValueError:
                continue
        
        return values
    
    def parse_summary_data(self, html_text: str) -> Dict[str, float]:
        """Parse summary statistics from the page."""
        summary = {}
        
        # Look for current statistics
        patterns = {
            'current_jobs': r'(?:Live jobs|Current vacancies).*?([\d,]+)',
            'median_salary': r'(?:Median salary|Average salary).*?£([\d,]+)',
            'market_share': r'(?:Market share|Percentage).*?(\d+\.?\d*)%'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, html_text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    summary[key] = float(value_str)
                except ValueError:
                    pass
        
        return summary