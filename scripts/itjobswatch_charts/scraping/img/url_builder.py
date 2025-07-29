"""
URL construction utilities for ITJobsWatch chart scraping.
"""

from typing import List, Dict, Tuple
from .config import BASE_URL, SKILLS, LOCATIONS, CHART_TYPES, JOB_TYPES, TIME_PERIODS


def build_chart_url(skill: str, location: str = "uk", chart_type: str = "demand-trend", 
                   job_type: str = "permanent", time_period: str = "m2x") -> str:
    """
    Build a complete ITJobsWatch chart URL.
    
    Args:
        skill: The skill/technology keyword (e.g., 'web-development')
        location: Geographic location (e.g., 'uk/england/london')
        chart_type: Type of chart (e.g., 'demand-trend')
        job_type: Type of job (e.g., 'permanent')
        time_period: Time period for the chart (e.g., 'm2x')
    
    Returns:
        Complete URL string for the WebP chart
    """
    url_parts = [
        BASE_URL,
        chart_type,
        job_type,
        time_period,
        location,
        f"{skill}.webp"
    ]
    
    return "/".join(url_parts)


def generate_filename(skill: str, location: str, chart_type: str, 
                     job_type: str, time_period: str) -> str:
    """
    Generate a simple filename for the downloaded WebP file.
    
    Args:
        skill: The skill/technology keyword
        location: Geographic location (unused for filename)
        chart_type: Type of chart (unused for filename)
        job_type: Type of job (unused for filename)
        time_period: Time period for the chart (unused for filename)
    
    Returns:
        Simple filename string (e.g., 'artificial-intelligence.webp')
    """
    return f"{skill}.webp"


def generate_all_urls() -> List[Tuple[str, str, Dict[str, str]]]:
    """
    Generate all possible URL combinations based on configuration.
    
    Returns:
        List of tuples: (url, filename, metadata_dict)
    """
    urls = []
    
    for skill in SKILLS:
        for location in LOCATIONS:
            for chart_type in CHART_TYPES:
                for job_type in JOB_TYPES:
                    for time_period in TIME_PERIODS:
                        url = build_chart_url(skill, location, chart_type, job_type, time_period)
                        filename = generate_filename(skill, location, chart_type, job_type, time_period)
                        
                        metadata = {
                            'skill': skill,
                            'location': location,
                            'chart_type': chart_type,
                            'job_type': job_type,
                            'time_period': time_period,
                            'url': url
                        }
                        
                        urls.append((url, filename, metadata))
    
    return urls


def generate_priority_urls() -> List[Tuple[str, str, Dict[str, str]]]:
    """
    Generate a smaller set of priority URLs for initial testing.
    
    Returns:
        List of tuples: (url, filename, metadata_dict)
    """
    priority_skills = ["web-development", "artificial-intelligence", "python", "javascript"]
    priority_locations = ["uk", "uk/england/london"]
    priority_chart_types = ["demand-trend"]
    priority_job_types = ["permanent"]
    priority_time_periods = ["m2x"]
    
    urls = []
    
    for skill in priority_skills:
        for location in priority_locations:
            for chart_type in priority_chart_types:
                for job_type in priority_job_types:
                    for time_period in priority_time_periods:
                        url = build_chart_url(skill, location, chart_type, job_type, time_period)
                        filename = generate_filename(skill, location, chart_type, job_type, time_period)
                        
                        metadata = {
                            'skill': skill,
                            'location': location,
                            'chart_type': chart_type,
                            'job_type': job_type,
                            'time_period': time_period,
                            'url': url
                        }
                        
                        urls.append((url, filename, metadata))
    
    return urls


def validate_url_components(skill: str, location: str, chart_type: str, 
                          job_type: str, time_period: str) -> bool:
    """
    Validate that URL components are in the allowed configuration lists.
    
    Returns:
        True if all components are valid, False otherwise
    """
    return (
        skill in SKILLS and
        location in LOCATIONS and
        chart_type in CHART_TYPES and
        job_type in JOB_TYPES and
        time_period in TIME_PERIODS
    )