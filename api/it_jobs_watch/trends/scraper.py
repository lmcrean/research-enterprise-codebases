"""Web scraper for ITJobsWatch historical trend data."""

import requests
import time
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup


class TrendScraper:
    """Scrapes historical trend data from ITJobsWatch technology pages."""
    
    def __init__(self, delay: float = 2.0):
        """Initialize scraper with rate limiting delay."""
        self.delay = delay
        self.base_url = 'https://www.itjobswatch.co.uk'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_technology_page(self, technology: str) -> Optional[str]:
        """Fetch the HTML content for a technology's trend page."""
        # Convert technology name to URL format
        url_technology = technology.lower().replace(' ', '%20')
        url = f'{self.base_url}/jobs/uk/{url_technology}.do'
        
        try:
            print(f"Fetching trends for: {technology}")
            response = self.session.get(url)
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.delay)
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {technology}: {str(e)}")
            return None
    
    def extract_chart_data(self, html: str) -> Dict[str, str]:
        """Extract JavaScript chart data from the HTML page."""
        soup = BeautifulSoup(html, 'html.parser')
        chart_data = {}
        
        # Find all script tags that might contain chart data
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                # Look for Highcharts data patterns
                if 'Highcharts.chart' in script.string or 'series:' in script.string:
                    # Extract job trends data
                    job_pattern = r'name:\s*[\'"]Jobs[\'"].*?data:\s*\[(.*?)\]'
                    job_match = re.search(job_pattern, script.string, re.DOTALL)
                    if job_match:
                        chart_data['jobs'] = job_match.group(1)
                    
                    # Extract salary trends data
                    salary_pattern = r'name:\s*[\'"]Salary[\'"].*?data:\s*\[(.*?)\]'
                    salary_match = re.search(salary_pattern, script.string, re.DOTALL)
                    if salary_match:
                        chart_data['salary'] = salary_match.group(1)
                    
                    # Extract categories (years/dates)
                    categories_pattern = r'categories:\s*\[(.*?)\]'
                    categories_match = re.search(categories_pattern, script.string, re.DOTALL)
                    if categories_match:
                        chart_data['categories'] = categories_match.group(1)
        
        # Alternative: Look for data in table format
        if not chart_data:
            chart_data = self._extract_table_data(soup)
        
        return chart_data
    
    def _extract_table_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract data from HTML tables as fallback."""
        table_data = {}
        
        # Look for trend summary tables
        summary_tables = soup.find_all('table', class_=['summary', 'trend', 'historical'])
        
        for table in summary_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].text.strip().lower()
                    value = cells[1].text.strip()
                    
                    if any(keyword in label for keyword in ['year', 'job', 'salary', 'trend']):
                        table_data[label] = value
        
        return table_data
    
    def get_technology_url(self, technology: str) -> str:
        """Generate the URL for a technology page."""
        url_technology = technology.lower().replace(' ', '%20')
        return f'{self.base_url}/jobs/uk/{url_technology}.do'