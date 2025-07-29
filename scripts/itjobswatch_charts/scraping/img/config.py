"""
Configuration for ITJobsWatch WebP chart scraping.
"""

SKILLS = [
    "web-development",
    "artificial-intelligence", 
    "csharp",
    "python",
    "typescript",
    "javascript",
    "software-engineering",
    "software-development",
    "data-analyst",
    "data-science",
    "data-scientist",
    "generative-ai",
    "rlhf",
    "it",
    "aws",
    "gcp",
    "asp.net"
]

LOCATIONS = [
    "uk",
    "uk/england/london",
    "uk/england/manchester",
    "uk/england/birmingham",
    "uk/england/leeds",
    "uk/england/bristol",
    "uk/england/cambridge",
    "uk/scotland/edinburgh",
    "uk/scotland/glasgow",
    "uk/wales/cardiff",
    "uk/northern-ireland/belfast"
]

CHART_TYPES = [
    "demand-trend",
    "salary-trend", 
    "skills-trend"
]

JOB_TYPES = [
    "permanent",
    "contract"
]

TIME_PERIODS = [
    "m2x",
    "m6x", 
    "y1x",
    "y5x"
]

BASE_URL = "https://www.itjobswatch.co.uk/charts"

RATE_LIMIT_DELAY = 1.0

OUTPUT_DIR = "data/scraped/itjobswatch"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

REQUEST_TIMEOUT = 30

MAX_RETRIES = 3