"""
Configuration for ITJobsWatch table data scraping.
"""

# Base URL for IT Jobs Watch
BASE_URL = "https://www.itjobswatch.co.uk/default.aspx"

# Request configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Output configuration
OUTPUT_DIR = "data/scraped/itjobswatch/table-data"

# Default search parameters
DEFAULT_PARAMS = {
    'q': '',        # Query (empty for all)
    'ql': '',       # Query location
    'll': 'London', # Location filter
    'id': '0',      # ID parameter
    'p': '1',       # Page number
    'e': '0',       # Employment type (0 = all)
    'sortby': '5',  # Sort by (5 = rank)
    'orderby': '0'  # Order (0 = ascending)
}

# Results per page (typically 50 on IT Jobs Watch)
RESULTS_PER_PAGE = 50

# Maximum pages to scrape (safety limit)
MAX_PAGES = 200

# Column mappings for the table data
COLUMN_MAPPINGS = {
    'skill_name': 'Description',
    'rank': 'Rank',
    'rank_change': 'Rank Change',
    'median_salary': 'Median Salary',
    'salary_change': 'Salary Year-on-Year Change',
    'historical_vacancies': 'Historical Job Vacancies',
    'live_jobs': 'Live Job Vacancies'
}