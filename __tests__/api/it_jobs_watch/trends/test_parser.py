"""Unit tests for ITJobsWatch trends parser."""

import pytest
from api.it_jobs_watch.trends.parser import TrendParser
from api.it_jobs_watch.trends.models import TrendDataPoint


class TestTrendParser:
    """Test cases for TrendParser."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.parser = TrendParser()
    
    def test_parse_empty_chart_data(self):
        """Test parsing empty chart data."""
        result = self.parser.parse_chart_data({})
        assert result == []
    
    def test_parse_categories_year_only(self):
        """Test parsing year-only categories."""
        categories_str = '"2021", "2022", "2023", "2024"'
        result = self.parser._parse_categories(categories_str)
        
        assert len(result) == 4
        assert result[0] == (2021, None)
        assert result[1] == (2022, None)
        assert result[2] == (2023, None)
        assert result[3] == (2024, None)
    
    def test_parse_categories_month_year(self):
        """Test parsing month-year categories."""
        categories_str = '"Jan 2023", "Feb 2023", "Mar 2023"'
        result = self.parser._parse_categories(categories_str)
        
        assert len(result) == 3
        assert result[0] == (2023, 1)
        assert result[1] == (2023, 2)
        assert result[2] == (2023, 3)
    
    def test_parse_categories_numeric_format(self):
        """Test parsing numeric month/year format."""
        categories_str = '"01/2023", "02/2023", "12/2023"'
        result = self.parser._parse_categories(categories_str)
        
        assert len(result) == 3
        assert result[0] == (2023, 1)
        assert result[1] == (2023, 2)
        assert result[2] == (2023, 12)
    
    def test_parse_date_string(self):
        """Test parsing various date string formats."""
        # Year only
        assert self.parser._parse_date_string("2023") == (2023, None)
        
        # Month Year
        assert self.parser._parse_date_string("Jan 2023") == (2023, 1)
        assert self.parser._parse_date_string("December 2023") == (2023, 12)
        
        # Numeric format
        assert self.parser._parse_date_string("01/2023") == (2023, 1)
        assert self.parser._parse_date_string("12/2023") == (2023, 12)
        
        # Invalid format
        assert self.parser._parse_date_string("invalid") == (None, None)
    
    def test_month_to_number(self):
        """Test month name to number conversion."""
        assert self.parser._month_to_number("jan") == 1
        assert self.parser._month_to_number("January") == 1
        assert self.parser._month_to_number("DEC") == 12
        assert self.parser._month_to_number("december") == 12
        assert self.parser._month_to_number("invalid") is None
    
    def test_parse_data_array(self):
        """Test parsing JavaScript data arrays."""
        # Simple array
        data_str = "1000, 2000, 3000, 4000"
        result = self.parser._parse_data_array(data_str)
        assert result == [1000.0, 2000.0, 3000.0, 4000.0]
        
        # Array with decimals
        data_str = "1000.5, 2000.75, 3000.25"
        result = self.parser._parse_data_array(data_str)
        assert result == [1000.5, 2000.75, 3000.25]
        
        # Array with negative numbers
        data_str = "-100, 200, -300, 400"
        result = self.parser._parse_data_array(data_str)
        assert result == [-100.0, 200.0, -300.0, 400.0]
        
        # Empty string
        assert self.parser._parse_data_array("") == []
    
    def test_parse_chart_data_with_jobs(self):
        """Test parsing chart data with job counts."""
        chart_data = {
            'categories': '"2022", "2023", "2024"',
            'jobs': '5000, 6000, 7000'
        }
        
        result = self.parser.parse_chart_data(chart_data)
        
        assert len(result) == 3
        assert all(isinstance(dp, TrendDataPoint) for dp in result)
        
        # Check first data point
        assert result[0].year == 2022
        assert result[0].value == 5000.0
        assert result[0].data_type == "job_count"
        
        # Check last data point
        assert result[2].year == 2024
        assert result[2].value == 7000.0
    
    def test_parse_chart_data_with_salary(self):
        """Test parsing chart data with salary information."""
        chart_data = {
            'categories': '"2022", "2023"',
            'salary': '70000, 75000'
        }
        
        result = self.parser.parse_chart_data(chart_data)
        
        assert len(result) == 2
        assert result[0].data_type == "median_salary"
        assert result[0].value == 70000.0
        assert result[1].value == 75000.0
    
    def test_parse_chart_data_mixed(self):
        """Test parsing chart data with both jobs and salary."""
        chart_data = {
            'categories': '"2022", "2023"',
            'jobs': '5000, 6000',
            'salary': '70000, 75000'
        }
        
        result = self.parser.parse_chart_data(chart_data)
        
        assert len(result) == 4  # 2 job points + 2 salary points
        
        job_points = [dp for dp in result if dp.data_type == "job_count"]
        salary_points = [dp for dp in result if dp.data_type == "median_salary"]
        
        assert len(job_points) == 2
        assert len(salary_points) == 2
    
    def test_parse_summary_data(self):
        """Test parsing summary statistics from HTML."""
        html_text = """
        <div>Live jobs: 1,234</div>
        <div>Median salary: £65,000</div>
        <div>Market share: 3.5%</div>
        """
        
        result = self.parser.parse_summary_data(html_text)
        
        assert result['current_jobs'] == 1234.0
        assert result['median_salary'] == 65000.0
        assert result['market_share'] == 3.5
    
    def test_parse_summary_data_case_insensitive(self):
        """Test parsing is case insensitive."""
        html_text = """
        <div>LIVE JOBS: 500</div>
        <div>Average Salary: £80,000</div>
        <div>PERCENTAGE: 2.5%</div>
        """
        
        result = self.parser.parse_summary_data(html_text)
        
        assert result['current_jobs'] == 500.0
        assert result['median_salary'] == 80000.0
        assert result['market_share'] == 2.5