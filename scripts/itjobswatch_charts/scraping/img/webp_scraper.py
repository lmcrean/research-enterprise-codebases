"""
WebP chart scraper for ITJobsWatch.
Downloads WebP chart images and saves them with metadata.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    OUTPUT_DIR, USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES, RATE_LIMIT_DELAY
)
from url_builder import generate_all_urls, generate_priority_urls


class WebPScraper:
    """WebP chart scraper for ITJobsWatch."""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.base_output_dir = Path(output_dir)
        self.session = self._create_session()
        self.logger = self._setup_logging()
        
        # Create base output directory
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'downloaded': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0
        }
    
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
            'Accept': 'image/webp,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('webp_scraper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_file = self.base_output_dir / 'scraper.log'
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
    
    def download_webp(self, url: str, filename: str, metadata: Dict) -> bool:
        """
        Download a single WebP file.
        
        Args:
            url: URL to download
            filename: Local filename to save as
            metadata: Metadata dictionary for the file
        
        Returns:
            True if successful, False otherwise
        """
        # Create directory path based on location and chart type
        location_short = metadata['location'].split('/')[-1] if '/' in metadata['location'] else metadata['location']
        chart_dir = f"{location_short}-{metadata['chart_type']}"
        output_dir = self.base_output_dir / chart_dir / "charts"
        metadata_dir = output_dir / "file-data"
        
        # Create directories
        output_dir.mkdir(parents=True, exist_ok=True)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            self.logger.info(f"Skipping existing file: {filename}")
            self.stats['skipped'] += 1
            return True
        
        try:
            self.logger.info(f"Downloading: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Check if response is actually a WebP image
            if not response.headers.get('content-type', '').startswith('image/'):
                self.logger.warning(f"Unexpected content type for {url}: {response.headers.get('content-type')}")
                self.stats['errors'] += 1
                return False
            
            # Save the WebP file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Save metadata in file-data subdirectory
            metadata_file = metadata_dir / f"{filepath.stem}.json"
            metadata_with_download = metadata.copy()
            metadata_with_download.update({
                'downloaded_at': datetime.now().isoformat(),
                'file_size': len(response.content),
                'content_type': response.headers.get('content-type'),
                'status_code': response.status_code
            })
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_with_download, f, indent=2)
            
            self.logger.info(f"Successfully downloaded: {filename} ({len(response.content)} bytes)")
            self.stats['downloaded'] += 1
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}: {e}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {url}: {e}")
            self.stats['errors'] += 1
            return False
    
    def scrape_priority_charts(self) -> None:
        """Scrape a priority subset of charts for testing."""
        urls = generate_priority_urls()
        self.stats['total'] = len(urls)
        
        self.logger.info(f"Starting priority scrape of {len(urls)} charts...")
        
        for i, (url, filename, metadata) in enumerate(urls, 1):
            self.logger.info(f"Progress: {i}/{len(urls)}")
            
            self.download_webp(url, filename, metadata)
            
            # Rate limiting
            if i < len(urls):  # Don't delay after the last request
                time.sleep(RATE_LIMIT_DELAY)
        
        self._log_final_stats()
    
    def scrape_all_charts(self) -> None:
        """Scrape all possible chart combinations."""
        urls = generate_all_urls()
        self.stats['total'] = len(urls)
        
        self.logger.info(f"Starting full scrape of {len(urls)} charts...")
        
        for i, (url, filename, metadata) in enumerate(urls, 1):
            self.logger.info(f"Progress: {i}/{len(urls)}")
            
            self.download_webp(url, filename, metadata)
            
            # Rate limiting
            if i < len(urls):  # Don't delay after the last request
                time.sleep(RATE_LIMIT_DELAY)
        
        self._log_final_stats()
    
    def scrape_custom_urls(self, url_list: List[Tuple[str, str, Dict]]) -> None:
        """Scrape a custom list of URLs."""
        self.stats['total'] = len(url_list)
        
        self.logger.info(f"Starting custom scrape of {len(url_list)} charts...")
        
        for i, (url, filename, metadata) in enumerate(url_list, 1):
            self.logger.info(f"Progress: {i}/{len(url_list)}")
            
            self.download_webp(url, filename, metadata)
            
            # Rate limiting
            if i < len(url_list):  # Don't delay after the last request
                time.sleep(RATE_LIMIT_DELAY)
        
        self._log_final_stats()
    
    def _log_final_stats(self) -> None:
        """Log final scraping statistics."""
        self.logger.info("Scraping completed!")
        self.logger.info(f"Total URLs: {self.stats['total']}")
        self.logger.info(f"Downloaded: {self.stats['downloaded']}")
        self.logger.info(f"Skipped (existing): {self.stats['skipped']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        
        # Save stats to file
        stats_file = self.base_output_dir / 'scrape_stats.json'
        stats_with_timestamp = self.stats.copy()
        stats_with_timestamp['completed_at'] = datetime.now().isoformat()
        
        with open(stats_file, 'w') as f:
            json.dump(stats_with_timestamp, f, indent=2)


def main():
    """Main function for running the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ITJobsWatch WebP Chart Scraper')
    parser.add_argument('--mode', choices=['priority', 'all', 'test'], 
                       default='priority', help='Scraping mode')
    parser.add_argument('--output-dir', default=OUTPUT_DIR, 
                       help='Output directory for downloaded files')
    
    args = parser.parse_args()
    
    scraper = WebPScraper(output_dir=args.output_dir)
    
    if args.mode == 'priority':
        scraper.scrape_priority_charts()
    elif args.mode == 'all':
        scraper.scrape_all_charts()
    elif args.mode == 'test':
        # Test with just one URL
        from url_builder import build_chart_url, generate_filename
        url = build_chart_url('web-development', 'uk/england/london')
        filename = generate_filename('web-development', 'uk/england/london', 
                                   'demand-trend', 'permanent', 'm2x')
        metadata = {
            'skill': 'web-development',
            'location': 'uk/england/london',
            'chart_type': 'demand-trend',
            'job_type': 'permanent',
            'time_period': 'm2x',
            'url': url
        }
        scraper.scrape_custom_urls([(url, filename, metadata)])


if __name__ == '__main__':
    main()