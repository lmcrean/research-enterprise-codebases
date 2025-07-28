"""Integration tests for IT Jobs Watch API."""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from api.itjobswatch.client import ITJobsWatchClient
from api.itjobswatch.collector import ITJobsWatchCollector
from api.itjobswatch.models import JobMarketStats, JobMarketMetadata


class TestITJobsWatchClient:
    """Test the IT Jobs Watch client functionality."""
    
    def test_client_initialization(self):
        """Test client initializes correctly."""
        client = ITJobsWatchClient()
        assert client.delay == 1.5
        assert client.base_url == 'https://www.itjobswatch.co.uk'
        assert 'User-Agent' in client.session.headers
    
    def test_client_with_custom_delay(self):
        """Test client with custom delay setting."""
        client = ITJobsWatchClient(delay=2.0)
        assert client.delay == 2.0
    
    def test_clean_text_utility(self):
        """Test text cleaning utility method."""
        client = ITJobsWatchClient()
        
        # Test whitespace normalization
        assert client._clean_text("  multiple   spaces  ") == "multiple spaces"
        assert client._clean_text("\t\nPython\n\t") == "Python"
    
    def test_parse_int_utility(self):
        """Test integer parsing utility method."""
        client = ITJobsWatchClient()
        
        assert client._parse_int("123") == 123
        assert client._parse_int("1,234") == 1234
        assert client._parse_int("-") == -1
        assert client._parse_int("") == -1
        assert client._parse_int("abc") == -1
    
    def test_parse_salary_utility(self):
        """Test salary parsing utility method."""
        client = ITJobsWatchClient()
        
        assert client._parse_salary("£50k") == 50000
        assert client._parse_salary("£75,000") == 75000
        assert client._parse_salary("60k") == 60000
        assert client._parse_salary("-") == -1
        assert client._parse_salary("") == -1
    
    def test_parse_rank_change_utility(self):
        """Test rank change parsing utility method.""" 
        client = ITJobsWatchClient()
        
        assert client._parse_rank_change("↑5") == 5
        assert client._parse_rank_change("↓3") == -3
        assert client._parse_rank_change("+2") == 2
        assert client._parse_rank_change("-4") == -4
        assert client._parse_rank_change("0") == 0
        assert client._parse_rank_change("-") == 0


class TestJobMarketModels:
    """Test the job market data models."""
    
    def test_job_market_stats_creation(self):
        """Test JobMarketStats model creation."""
        stats = JobMarketStats(
            technology="Python",
            demand_rank=5,
            rank_change=2,
            median_salary=65000,
            salary_change="+5%",
            total_vacancies=1500,
            live_jobs=300,
            location="London",
            collected_at="2024-01-15"
        )
        
        assert stats.technology == "Python"
        assert stats.demand_rank == 5
        assert stats.median_salary == 65000
        assert stats.location == "London"
    
    def test_job_market_stats_to_dict(self):
        """Test JobMarketStats dictionary conversion."""
        stats = JobMarketStats(
            technology="C#",
            demand_rank=8,
            rank_change=-1,
            median_salary=70000,
            salary_change="+3%",
            total_vacancies=1200,
            live_jobs=250,
            location="London",
            collected_at="2024-01-15"
        )
        
        data_dict = stats.to_dict()
        
        assert data_dict['Technology'] == "C#"
        assert data_dict['Demand Rank'] == 8
        assert data_dict['Median Salary'] == 70000
        assert data_dict['Location'] == "London"
    
    def test_job_market_metadata_creation(self):
        """Test JobMarketMetadata creation."""
        metadata = JobMarketMetadata.create(
            tech_count=5,
            location="London", 
            collection_time=45.5
        )
        
        assert metadata.total_technologies == 5
        assert metadata.location == "London"
        assert metadata.collection_time_seconds == 45.5
        assert metadata.last_updated is not None


class TestITJobsWatchCollector:
    """Test the data collection orchestrator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_collector_initialization(self):
        """Test collector initializes correctly."""
        technologies = ["Python", "C#"]
        collector = ITJobsWatchCollector(technologies)
        
        assert collector.technologies == technologies
        assert collector.output_dir == "data/raw"
        assert isinstance(collector.client, ITJobsWatchClient)
    
    def test_collector_with_custom_output_dir(self):
        """Test collector with custom output directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            technologies = ["TypeScript"]
            collector = ITJobsWatchCollector(technologies, output_dir=temp_dir)
            
            assert collector.output_dir == temp_dir
            assert os.path.exists(temp_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    @patch('api.itjobswatch.collector.ITJobsWatchClient')
    def test_save_to_csv(self, mock_client_class):
        """Test CSV saving functionality."""
        temp_dir = tempfile.mkdtemp()
        try:
            collector = ITJobsWatchCollector(["Python"], output_dir=temp_dir)
            
            # Create test data
            stats = [
                JobMarketStats(
                    technology="Python Developer",
                    demand_rank=5,
                    rank_change=1,
                    median_salary=65000,
                    salary_change="+5%",
                    total_vacancies=1500,
                    live_jobs=300,
                    location="London",
                    collected_at="2024-01-15"
                )
            ]
            
            csv_path = os.path.join(temp_dir, "test.csv")
            collector._save_to_csv(stats, csv_path)
            
            assert os.path.exists(csv_path)
            
            # Verify CSV content
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Technology' in content
                assert 'Python Developer' in content
                assert '65000' in content
                
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])