"""Unit tests for ITJobsWatch trends models."""

import pytest
from datetime import datetime
from api.it_jobs_watch.trends.models import TrendDataPoint, TechnologyTrend, TrendCollection


class TestTrendDataPoint:
    """Test cases for TrendDataPoint model."""
    
    def test_create_basic_data_point(self):
        """Test creating a basic trend data point."""
        dp = TrendDataPoint(year=2023, value=1500.0)
        assert dp.year == 2023
        assert dp.value == 1500.0
        assert dp.month is None
        assert dp.data_type == "job_count"
    
    def test_create_full_data_point(self):
        """Test creating a data point with all fields."""
        dp = TrendDataPoint(year=2023, value=75000.0, month=6, data_type="median_salary")
        assert dp.year == 2023
        assert dp.value == 75000.0
        assert dp.month == 6
        assert dp.data_type == "median_salary"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        dp = TrendDataPoint(year=2023, value=1500.0, month=3, data_type="job_count")
        result = dp.to_dict()
        
        assert result == {
            'year': 2023,
            'month': 3,
            'value': 1500.0,
            'type': 'job_count'
        }


class TestTechnologyTrend:
    """Test cases for TechnologyTrend model."""
    
    def test_create_technology_trend(self):
        """Test creating a technology trend."""
        trend = TechnologyTrend(technology="Python")
        assert trend.technology == "Python"
        assert trend.data_points == []
        assert trend.url is None
        assert trend.last_updated is None
    
    def test_add_data_point(self):
        """Test adding data points to a trend."""
        trend = TechnologyTrend(technology="Python")
        trend.add_data_point(2022, 5000.0)
        trend.add_data_point(2023, 6000.0, "job_count", 6)
        
        assert len(trend.data_points) == 2
        assert trend.data_points[0].year == 2022
        assert trend.data_points[0].value == 5000.0
        assert trend.data_points[1].month == 6
    
    def test_get_data_by_type(self):
        """Test filtering data points by type."""
        trend = TechnologyTrend(technology="Python")
        trend.add_data_point(2022, 5000.0, "job_count")
        trend.add_data_point(2022, 70000.0, "median_salary")
        trend.add_data_point(2023, 6000.0, "job_count")
        
        job_data = trend.get_data_by_type("job_count")
        assert len(job_data) == 2
        assert all(dp.data_type == "job_count" for dp in job_data)
        
        salary_data = trend.get_data_by_type("median_salary")
        assert len(salary_data) == 1
        assert salary_data[0].value == 70000.0
    
    def test_get_years_range(self):
        """Test getting min and max years."""
        trend = TechnologyTrend(technology="Python")
        
        # Empty trend
        assert trend.get_years_range() == (None, None)
        
        # Add data points
        trend.add_data_point(2020, 3000.0)
        trend.add_data_point(2023, 6000.0)
        trend.add_data_point(2021, 4000.0)
        
        assert trend.get_years_range() == (2020, 2023)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        trend = TechnologyTrend(
            technology="Python",
            url="https://example.com",
            last_updated="2023-12-01"
        )
        trend.add_data_point(2023, 5000.0)
        
        result = trend.to_dict()
        assert result['technology'] == "Python"
        assert result['url'] == "https://example.com"
        assert result['last_updated'] == "2023-12-01"
        assert len(result['data_points']) == 1


class TestTrendCollection:
    """Test cases for TrendCollection model."""
    
    def test_create_collection(self):
        """Test creating a trend collection."""
        collection = TrendCollection()
        assert collection.trends == {}
        assert isinstance(collection.collection_date, str)
    
    def test_add_technology(self):
        """Test adding technologies to collection."""
        collection = TrendCollection()
        
        # Add new technology
        trend = collection.add_technology("Python", "https://example.com/python")
        assert "Python" in collection.trends
        assert trend.technology == "Python"
        assert trend.url == "https://example.com/python"
        
        # Add existing technology (should return existing)
        trend2 = collection.add_technology("Python")
        assert trend2 is trend
    
    def test_get_technology(self):
        """Test getting technology from collection."""
        collection = TrendCollection()
        collection.add_technology("Python")
        
        trend = collection.get_technology("Python")
        assert trend is not None
        assert trend.technology == "Python"
        
        assert collection.get_technology("Java") is None
    
    def test_get_all_technologies(self):
        """Test getting list of all technologies."""
        collection = TrendCollection()
        collection.add_technology("Python")
        collection.add_technology("Java")
        collection.add_technology("JavaScript")
        
        techs = collection.get_all_technologies()
        assert len(techs) == 3
        assert "Python" in techs
        assert "Java" in techs
        assert "JavaScript" in techs
    
    def test_to_dataframe_format(self):
        """Test conversion to DataFrame format."""
        collection = TrendCollection()
        
        # Add Python data
        python_trend = collection.add_technology("Python", "https://example.com/python")
        python_trend.add_data_point(2022, 5000.0, "job_count")
        python_trend.add_data_point(2023, 6000.0, "job_count")
        
        # Add Java data
        java_trend = collection.add_technology("Java", "https://example.com/java")
        java_trend.add_data_point(2022, 4000.0, "job_count")
        
        rows = collection.to_dataframe_format()
        assert len(rows) == 3
        
        # Check first row
        assert rows[0]['Technology'] == "Python"
        assert rows[0]['Year'] == 2022
        assert rows[0]['Value'] == 5000.0
        assert rows[0]['Type'] == "job_count"