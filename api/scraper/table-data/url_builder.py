"""
URL builder for ITJobsWatch table data endpoints.
"""

from typing import Dict, Optional
from urllib.parse import urlencode
from .config import BASE_URL, DEFAULT_PARAMS


def build_table_url(
    location: str = "London",
    page: int = 1,
    query: Optional[str] = None,
    sort_by: int = 5,
    order_by: int = 0
) -> str:
    """
    Build URL for IT Jobs Watch table data.
    
    Args:
        location: Location filter (e.g., "London", "Manchester")
        page: Page number (1-based)
        query: Search query (optional)
        sort_by: Sort field (5 = rank)
        order_by: Sort order (0 = ascending)
    
    Returns:
        Complete URL for the table data page
    """
    params = DEFAULT_PARAMS.copy()
    
    # Update parameters
    params['ll'] = location
    params['p'] = str(page)
    params['sortby'] = str(sort_by)
    params['orderby'] = str(order_by)
    
    if query:
        params['q'] = query
    
    # Build the complete URL
    url = f"{BASE_URL}?{urlencode(params)}"
    return url


def build_pagination_urls(
    location: str = "London",
    total_pages: int = 1,
    query: Optional[str] = None,
    sort_by: int = 5,
    order_by: int = 0
) -> list:
    """
    Build URLs for all pages of results.
    
    Args:
        location: Location filter
        total_pages: Total number of pages to generate
        query: Search query (optional)
        sort_by: Sort field
        order_by: Sort order
    
    Returns:
        List of URLs for all pages
    """
    urls = []
    
    for page in range(1, total_pages + 1):
        url = build_table_url(
            location=location,
            page=page,
            query=query,
            sort_by=sort_by,
            order_by=order_by
        )
        urls.append(url)
    
    return urls


def parse_url_params(url: str) -> Dict[str, str]:
    """
    Parse parameters from an IT Jobs Watch URL.
    
    Args:
        url: URL to parse
    
    Returns:
        Dictionary of URL parameters
    """
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    # Convert lists to single values
    result = {}
    for key, value in params.items():
        result[key] = value[0] if value else ''
    
    return result