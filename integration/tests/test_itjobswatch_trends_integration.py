"""Integration tests for ITJobsWatch trends functionality."""

import os
import sys
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.it_jobs_watch.trends.models import TrendCollection
from api.it_jobs_watch.trends.scraper import TrendScraper
from api.it_jobs_watch.trends.parser import TrendParser
from scripts.itjobswatch_trends.collector import TrendCollector
from scripts.itjobswatch_trends.visualizer import TrendVisualizer
from scripts.itjobswatch_trends.exporter import TrendExporter


class TestITJobsWatchTrendsIntegration:
    """Integration tests for the complete trends pipeline."""
    
    def test_models_integration(self):
        """Test that models work together correctly."""
        collection = TrendCollection()
        
        # Add multiple technologies
        python_trend = collection.add_technology("Python", "https://example.com/python")
        java_trend = collection.add_technology("Java", "https://example.com/java")
        
        # Add data points
        for year in range(2020, 2024):
            python_trend.add_data_point(year, 5000 + year * 500, "job_count")
            java_trend.add_data_point(year, 4000 + year * 400, "job_count")
        
        # Test collection methods
        assert len(collection.get_all_technologies()) == 2
        assert collection.get_technology("Python") is not None
        
        # Test DataFrame conversion
        df_data = collection.to_dataframe_format()
        assert len(df_data) == 8  # 4 years * 2 technologies
    
    def test_scraper_parser_integration(self):
        """Test that scraper and parser work together."""
        scraper = TrendScraper(delay=0.1)
        parser = TrendParser()
        
        # Test with sample HTML
        sample_html = '''
        <html>
        <script>
        Highcharts.chart('container', {
            xAxis: {
                categories: ['2022', '2023', '2024']
            },
            series: [{
                name: 'Jobs',
                data: [5000, 6000, 7000]
            }]
        });
        </script>
        </html>
        '''
        
        # Extract and parse
        chart_data = scraper.extract_chart_data(sample_html)
        data_points = parser.parse_chart_data(chart_data)
        
        assert len(data_points) == 3
        assert data_points[0].year == 2022
        assert data_points[0].value == 5000.0
    
    def test_collector_with_demo_data(self):
        """Test the collector with demo data generation."""
        collector = TrendCollector()
        
        # Override to use only one technology for speed
        collector.TECHNOLOGIES = ["Python"]
        
        # Collect trends (will use demo data)
        collection = collector.collect_all_trends()
        
        assert "Python" in collection.get_all_technologies()
        python_trend = collection.get_technology("Python")
        assert len(python_trend.data_points) > 0
    
    def test_visualizer_integration(self, tmp_path):
        """Test visualization generation."""
        # Create test data
        collection = TrendCollection()
        trend = collection.add_technology("Test Tech")
        for year in range(2020, 2024):
            trend.add_data_point(year, 1000 * year, "job_count")
        
        # Generate chart
        visualizer = TrendVisualizer()
        chart_path = tmp_path / "test_chart.png"
        
        visualizer.create_trend_chart(collection, str(chart_path))
        
        assert chart_path.exists()
        assert chart_path.stat().st_size > 0
    
    def test_exporter_integration(self, tmp_path):
        """Test data export functionality."""
        # Create test data
        collection = TrendCollection()
        trend = collection.add_technology("Test Tech")
        for year in range(2020, 2024):
            trend.add_data_point(year, 1000 * year, "job_count")
        
        # Export data
        exporter = TrendExporter()
        csv_path = tmp_path / "test_data.csv"
        
        exporter.export_to_csv(collection, str(csv_path))
        
        assert csv_path.exists()
        
        # Check raw file was also created
        raw_path = tmp_path / "test_data_raw.csv"
        assert raw_path.exists()
    
    def test_end_to_end_pipeline(self, tmp_path):
        """Test the complete pipeline from collection to output."""
        # Setup
        collector = TrendCollector()
        collector.TECHNOLOGIES = ["Python", "Java"]  # Limited for test speed
        visualizer = TrendVisualizer()
        exporter = TrendExporter()
        
        # Collect data
        collection = collector.collect_all_trends()
        
        # Generate outputs
        chart_path = tmp_path / "trends.png"
        csv_path = tmp_path / "trends.csv"
        
        visualizer.create_trend_chart(collection, str(chart_path))
        exporter.export_to_csv(collection, str(csv_path))
        
        # Verify outputs
        assert chart_path.exists()
        assert csv_path.exists()
        assert (tmp_path / "trends_raw.csv").exists()
        
        # Verify data integrity
        assert len(collection.get_all_technologies()) == 2
        
        for tech in ["Python", "Java"]:
            trend = collection.get_technology(tech)
            assert trend is not None
            assert len(trend.data_points) > 0
    
    def test_error_handling(self):
        """Test error handling in the pipeline."""
        scraper = TrendScraper()
        parser = TrendParser()
        
        # Test with invalid HTML
        result = scraper.extract_chart_data("")
        assert isinstance(result, dict)
        
        # Test parser with invalid data
        data_points = parser.parse_chart_data({})
        assert data_points == []
        
        # Test with mismatched data lengths
        chart_data = {
            'categories': '"2022", "2023"',
            'jobs': '5000, 6000, 7000'  # More values than categories
        }
        data_points = parser.parse_chart_data(chart_data)
        assert len(data_points) == 2  # Should only use matching pairs