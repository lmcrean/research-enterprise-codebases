"""Unit tests for ITJobsWatch trends scraper."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from api.it_jobs_watch.trends.scraper import TrendScraper


class TestTrendScraper:
    """Test cases for TrendScraper."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.scraper = TrendScraper(delay=0.1)  # Short delay for tests
    
    def test_init(self):
        """Test scraper initialization."""
        scraper = TrendScraper(delay=2.0)
        assert scraper.delay == 2.0
        assert scraper.base_url == 'https://www.itjobswatch.co.uk'
        assert 'User-Agent' in scraper.session.headers
    
    @patch('requests.Session.get')
    def test_fetch_technology_page_success(self, mock_get):
        """Test successful page fetch."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Test content</body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_technology_page('Python')
        
        assert result == '<html><body>Test content</body></html>'
        mock_get.assert_called_once()
        
        # Check URL construction
        call_args = mock_get.call_args
        assert 'python.do' in call_args[0][0].lower()
    
    @patch('requests.Session.get')
    def test_fetch_technology_page_with_spaces(self, mock_get):
        """Test fetching page for technology with spaces."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        self.scraper.fetch_technology_page('Data Science')
        
        # Check URL encoding
        call_args = mock_get.call_args
        assert 'data%20science.do' in call_args[0][0].lower()
    
    @patch('requests.Session.get')
    def test_fetch_technology_page_error(self, mock_get):
        """Test handling fetch errors."""
        # Mock 404 error
        mock_get.side_effect = requests.exceptions.HTTPError('404 Not Found')
        
        result = self.scraper.fetch_technology_page('InvalidTech')
        
        assert result is None
    
    def test_extract_chart_data_with_highcharts(self):
        """Test extracting chart data from Highcharts script."""
        html = '''
        <html>
        <script>
        Highcharts.chart('container', {
            series: [{
                name: 'Jobs',
                data: [1000, 2000, 3000]
            }],
            xAxis: {
                categories: ['2021', '2022', '2023']
            }
        });
        </script>
        </html>
        '''
        
        result = self.scraper.extract_chart_data(html)
        
        assert 'jobs' in result
        assert 'categories' in result
        assert '1000, 2000, 3000' in result['jobs']
        assert '2021' in result['categories']
    
    def test_extract_chart_data_with_salary(self):
        """Test extracting salary data from charts."""
        html = '''
        <html>
        <script>
        var chart = {
            series: [{
                name: 'Salary',
                data: [70000, 75000, 80000]
            }]
        };
        </script>
        </html>
        '''
        
        result = self.scraper.extract_chart_data(html)
        
        assert 'salary' in result
        assert '70000, 75000, 80000' in result['salary']
    
    def test_extract_chart_data_no_script(self):
        """Test extracting data when no script tags exist."""
        html = '<html><body>No scripts here</body></html>'
        
        result = self.scraper.extract_chart_data(html)
        
        # Should fall back to table extraction
        assert isinstance(result, dict)
    
    def test_extract_table_data(self):
        """Test extracting data from HTML tables."""
        from bs4 import BeautifulSoup
        
        html = '''
        <table class="summary">
            <tr>
                <td>Year</td>
                <td>2023</td>
            </tr>
            <tr>
                <td>Jobs</td>
                <td>5000</td>
            </tr>
            <tr>
                <td>Median Salary</td>
                <td>£70,000</td>
            </tr>
        </table>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_table_data(soup)
        
        assert 'year' in result
        assert result['year'] == '2023'
        assert 'jobs' in result
        assert result['jobs'] == '5000'
    
    def test_extract_table_data_no_tables(self):
        """Test extraction when no relevant tables exist."""
        from bs4 import BeautifulSoup
        
        html = '<html><body>No tables</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = self.scraper._extract_table_data(soup)
        
        assert result == {}
    
    def test_get_technology_url(self):
        """Test URL generation for technologies."""
        # Simple technology
        url = self.scraper.get_technology_url('Python')
        assert url == 'https://www.itjobswatch.co.uk/jobs/uk/python.do'
        
        # Technology with space
        url = self.scraper.get_technology_url('Data Science')
        assert url == 'https://www.itjobswatch.co.uk/jobs/uk/data%20science.do'
        
        # Technology with multiple words
        url = self.scraper.get_technology_url('Machine Learning Engineer')
        assert url == 'https://www.itjobswatch.co.uk/jobs/uk/machine%20learning%20engineer.do'
    
    @patch('time.sleep')
    @patch('requests.Session.get')
    def test_rate_limiting(self, mock_get, mock_sleep):
        """Test that rate limiting is applied."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        self.scraper.fetch_technology_page('Python')
        
        # Check that sleep was called with the delay
        mock_sleep.assert_called_once_with(self.scraper.delay)