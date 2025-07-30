"""
IT Jobs Watch table data scraper.
Scrapes job market statistics from ITJobsWatch listings.
"""

import os
import csv
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    BASE_URL, USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES, 
    RATE_LIMIT_DELAY, OUTPUT_DIR, RESULTS_PER_PAGE, MAX_PAGES
)
from .url_builder import build_table_url, parse_url_params
from .models import JobListing, ScrapeMetadata


class ITJobsWatchTableScraper:
    """Scraper for IT Jobs Watch table data."""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.session = self._create_session()
        self.logger = self._setup_logging()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('itjobswatch_table_scraper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_file = self.output_dir / 'table_scraper.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def _parse_table_row(self, row_element) -> Optional[Dict[str, str]]:
        """
        Parse a single table row from the HTML.
        
        Args:
            row_element: BeautifulSoup element for the row
        
        Returns:
            Dictionary with parsed data or None if parsing fails
        """
        try:
            # The data is in a structured format with specific column classes
            # c2: skill name, c3: rank, c4: rank change, c5: salary, c6: salary change, c7: historical, c8: live
            
            skill_cell = row_element.find('td', class_='c2')
            if not skill_cell:
                return None
            
            # Extract skill name
            skill_link = skill_cell.find('a')
            skill_name = skill_link.text.strip() if skill_link else skill_cell.text.strip()
            
            # Extract rank
            rank_cell = row_element.find('td', class_='c3')
            rank = rank_cell.text.strip() if rank_cell else '0'
            
            # Extract rank change
            rank_change_cell = row_element.find('td', class_='c4')
            rank_change = '0'
            if rank_change_cell:
                # The change is in the text after any span elements
                change_text = rank_change_cell.text.strip()
                if change_text and change_text != '0':
                    rank_change = change_text
            
            # Extract median salary
            salary_cell = row_element.find('td', class_='c5')
            median_salary = salary_cell.text.strip() if salary_cell else '-'
            
            # Extract salary change
            salary_change_cell = row_element.find('td', class_='c6')
            salary_change = salary_change_cell.text.strip() if salary_change_cell else '-'
            
            # Extract historical vacancies
            hist_cell = row_element.find('td', class_='c7')
            historical_vacancies = '-'
            if hist_cell:
                # Get the main number
                hist_text = hist_cell.contents[0].strip() if hist_cell.contents else ''
                # Get the percentage from span
                hist_span = hist_cell.find('span', class_='data-relative')
                hist_pct = hist_span.text.strip() if hist_span else ''
                if hist_text and hist_pct:
                    historical_vacancies = f"{hist_text} {hist_pct}"
                elif hist_text:
                    historical_vacancies = hist_text
            
            # Extract live jobs
            live_cell = row_element.find('td', class_='c8')
            live_jobs = '0'
            if live_cell:
                live_link = live_cell.find('a')
                live_jobs = live_link.text.strip() if live_link else live_cell.text.strip()
            
            self.logger.debug(f"Parsed: {skill_name}, rank={rank}, change={rank_change}, salary={median_salary}")
            
            return {
                'skill_name': skill_name,
                'rank': rank,
                'rank_change': rank_change,
                'median_salary': median_salary,
                'salary_change': salary_change,
                'historical_vacancies': historical_vacancies,
                'live_jobs': live_jobs
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing table row: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def _extract_total_results(self, soup: BeautifulSoup) -> int:
        """
        Extract total number of results from the page.
        
        Args:
            soup: BeautifulSoup object of the page
        
        Returns:
            Total number of results
        """
        try:
            # Look for results text like "Results 1 - 50 of 5,261"
            results_text = soup.find(text=lambda t: t and 'Results' in t and 'of' in t)
            if results_text:
                # Extract the total number
                parts = results_text.strip().split()
                if 'of' in parts:
                    total_index = parts.index('of') + 1
                    if total_index < len(parts):
                        total_str = parts[total_index].replace(',', '')
                        return int(total_str)
        except Exception as e:
            self.logger.error(f"Error extracting total results: {e}")
        
        return 0
    
    def scrape_page(self, url: str, location: str) -> Tuple[List[JobListing], int]:
        """
        Scrape a single page of results.
        
        Args:
            url: URL to scrape
            location: Location for the listings
        
        Returns:
            Tuple of (list of JobListing objects, total results count)
        """
        listings = []
        total_results = 0
        
        try:
            self.logger.info(f"Scraping page: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract total results on first page
            total_results = self._extract_total_results(soup)
            
            # Find the main results table
            # IT Jobs Watch uses a table structure for results
            table = soup.find('table', class_='results')
            
            if table:
                rows = table.find_all('tr')
                
                # Skip the header row
                for i, row in enumerate(rows):
                    if i == 0:  # Skip header
                        continue
                    
                    row_data = self._parse_table_row(row)
                    if row_data:
                        try:
                            listing = JobListing.from_row_data(row_data, location)
                            listings.append(listing)
                        except Exception as e:
                            self.logger.error(f"Error creating JobListing: {e}")
            else:
                self.logger.warning("Could not find results table on page")
            
            self.logger.info(f"Extracted {len(listings)} listings from page")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error scraping {url}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {e}")
        
        return listings, total_results
    
    def scrape_location(
        self, 
        location: str = "London",
        max_pages: Optional[int] = None,
        query: Optional[str] = None
    ) -> List[JobListing]:
        """
        Scrape all pages for a specific location.
        
        Args:
            location: Location to scrape
            max_pages: Maximum pages to scrape (None for all)
            query: Optional search query
        
        Returns:
            List of all JobListing objects
        """
        all_listings = []
        page = 1
        total_pages = 1
        
        metadata = ScrapeMetadata(
            location=location,
            total_records=0,
            total_pages=0,
            scrape_start=datetime.now(),
            scrape_end=datetime.now(),
            success=False
        )
        
        try:
            # First page to get total results
            url = build_table_url(location=location, page=1, query=query)
            listings, total_results = self.scrape_page(url, location)
            all_listings.extend(listings)
            
            # Calculate total pages
            if total_results > 0:
                total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
                
                # Apply max_pages limit
                if max_pages:
                    total_pages = min(total_pages, max_pages)
                
                total_pages = min(total_pages, MAX_PAGES)  # Safety limit
                
                self.logger.info(f"Total results: {total_results}, Total pages: {total_pages}")
                
                # Scrape remaining pages
                for page in range(2, total_pages + 1):
                    url = build_table_url(location=location, page=page, query=query)
                    listings, _ = self.scrape_page(url, location)
                    all_listings.extend(listings)
                    
                    # Rate limiting
                    time.sleep(RATE_LIMIT_DELAY)
            
            metadata.total_records = len(all_listings)
            metadata.total_pages = page
            metadata.success = True
            
        except Exception as e:
            self.logger.error(f"Error during location scrape: {e}")
            metadata.error_message = str(e)
        
        metadata.scrape_end = datetime.now()
        
        # Save metadata
        self._save_metadata(metadata, location)
        
        return all_listings
    
    def _save_metadata(self, metadata: ScrapeMetadata, location: str) -> None:
        """Save scraping metadata."""
        metadata_file = self.output_dir / f"{location.replace('/', '_')}_metadata.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def save_to_csv(self, listings: List[JobListing], filename: str) -> None:
        """
        Save listings to CSV file.
        
        Args:
            listings: List of JobListing objects
            filename: Output filename
        """
        filepath = self.output_dir / filename
        
        if not listings:
            self.logger.warning("No listings to save")
            return
        
        # Get field names from first listing
        fieldnames = list(listings[0].to_dict().keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for listing in listings:
                writer.writerow(listing.to_dict())
        
        self.logger.info(f"Saved {len(listings)} listings to {filepath}")


def main():
    """Main function for running the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='IT Jobs Watch Table Data Scraper')
    parser.add_argument('--location', default='London', help='Location to scrape')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to scrape')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--output', help='Output filename (default: location_jobs.csv)')
    
    args = parser.parse_args()
    
    scraper = ITJobsWatchTableScraper()
    
    # Scrape the data
    listings = scraper.scrape_location(
        location=args.location,
        max_pages=args.max_pages,
        query=args.query
    )
    
    # Determine output filename
    if args.output:
        filename = args.output
    else:
        location_safe = args.location.replace('/', '_').lower()
        filename = f"{location_safe}_jobs.csv"
    
    # Save to CSV
    scraper.save_to_csv(listings, filename)
    
    print(f"Scraping complete. Saved {len(listings)} listings to {filename}")


if __name__ == '__main__':
    main()