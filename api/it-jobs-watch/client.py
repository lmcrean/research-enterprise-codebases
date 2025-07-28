"""IT Jobs Watch web scraper client for job market data."""

import requests
import time
import re
from typing import Optional, List
from bs4 import BeautifulSoup
from .models import JobMarketStats


class ITJobsWatchClient:
    """Web scraper client for IT Jobs Watch with rate limiting."""
    
    def __init__(self, delay: float = 1.5):
        """Initialize client with rate limiting delay."""
        self.delay = delay
        self.base_url = 'https://www.itjobswatch.co.uk'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_london_job_stats(self, technology: str) -> List[JobMarketStats]:
        """Fetch job market statistics for a technology in London."""
        search_url = f'{self.base_url}/default.aspx'
        params = {
            'page': '1',
            'sortby': '0',
            'orderby': '0',
            'q': technology,
            'id': '0',
            'lid': '2649'  # London location ID
        }
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_stats = self._parse_job_data(soup, technology)
            
            # Rate limiting
            time.sleep(self.delay)
            
            return job_stats
            
        except Exception as e:
            print(f"❌ Error fetching data for {technology}: {str(e)}")
            return []
    
    def _parse_job_data(self, soup: BeautifulSoup, technology: str) -> List[JobMarketStats]:
        """Parse job market data from HTML table."""
        job_stats = []
        
        # Find the main results table
        table = soup.find('table', {'id': 'skills-table'}) or soup.find('table', class_='resultsTable')
        
        if not table:
            # Try alternative selectors
            table = soup.find('table')
        
        if not table:
            print(f"⚠️  No data table found for {technology}")
            return []
        
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 7:
                try:
                    job_title = self._clean_text(cells[0].text)
                    
                    # Skip if this doesn't match our technology search
                    if technology.lower() not in job_title.lower():
                        continue
                    
                    demand_rank = self._parse_int(cells[1].text)
                    rank_change = self._parse_rank_change(cells[2].text)
                    median_salary = self._parse_salary(cells[3].text)
                    salary_change = self._clean_text(cells[4].text)
                    total_vacancies = self._parse_int(cells[5].text)
                    live_jobs = self._parse_int(cells[6].text)
                    
                    stats = JobMarketStats(
                        technology=job_title,
                        demand_rank=demand_rank,
                        rank_change=rank_change,
                        median_salary=median_salary,
                        salary_change=salary_change,
                        total_vacancies=total_vacancies,
                        live_jobs=live_jobs,
                        location="London",
                        collected_at=time.strftime('%Y-%m-%d')
                    )
                    
                    job_stats.append(stats)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing row for {technology}: {str(e)}")
                    continue
        
        return job_stats
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _parse_int(self, text: str) -> int:
        """Parse integer from text, handling formatting."""
        clean_text = re.sub(r'[^\d-]', '', text.strip())
        try:
            return int(clean_text) if clean_text and clean_text != '-' else -1
        except ValueError:
            return -1
    
    def _parse_salary(self, text: str) -> int:
        """Parse salary from text, handling £ and k formatting."""
        clean_text = re.sub(r'[£,k]', '', text.strip().lower())
        try:
            salary = float(clean_text) if clean_text and clean_text != '-' else -1
            # Convert 'k' format to full number
            if 'k' in text.lower():
                salary *= 1000
            return int(salary)
        except ValueError:
            return -1
    
    def _parse_rank_change(self, text: str) -> int:
        """Parse rank change, handling up/down arrows and signs."""
        clean_text = re.sub(r'[^\d+-]', '', text.strip())
        try:
            if '↑' in text or '+' in text:
                return abs(int(clean_text)) if clean_text else 0
            elif '↓' in text or '-' in text:
                return -abs(int(clean_text)) if clean_text else 0
            else:
                return int(clean_text) if clean_text else 0
        except ValueError:
            return 0