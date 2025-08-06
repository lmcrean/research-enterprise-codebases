"""ITJobsWatch 2025 benchmark data for comparison."""

# Report 1: Programming Languages (2025 Market Share %)
PROGRAMMING_LANGUAGES = {
    'python': 18.52,
    'java': 8.02,
    'javascript': 7.21,
    'typescript': 5.79,
    'c#': 6.44,
    'csharp': 6.44  # Alternative spelling
}

# Report 2: Cloud & Technology Infrastructure (2025 Market Share %)
CLOUD_INFRASTRUCTURE = {
    'azure': 18.99,
    'aws': 15.69,
    'kubernetes': 6.25,
    'docker': 4.79,
    'terraform': 5.08,
    'gcp': 3.07
}

# Report 3: Job Titles (2025 Market Share %)
JOB_TITLES = {
    'analyst': 10.51,  # Broad analyst category
    'devops': 11.45,
    'software engineering': 8.35,
    'software engineer': 8.35,
    'cyber security': 7.47,
    'data analytics': 7.12,
    'data analyst': 7.12,
    'data science': 6.58,
    'data scientist': 6.58,
    'web development': 4.52,
    'web developer': 4.52,
    'software developer': 8.35  # Grouping with software engineering
}

# Report 4: Themes & Sectors (2025 Market Share %)
THEMES_SECTORS = {
    'finance': 33.53,
    'artificial intelligence': 11.46,
    'ai': 11.46,
    'marketing': 8.45,
    'risk management': 7.30,
    'machine learning': 6.52,
    'ml': 6.52,
    'business intelligence': 5.85,
    'bi': 5.85,
    'customer service': 2.75,
    'law': 1.82
}

# Report 5: Themes & Sectors Excluding Finance (2025 Market Share %)
# These are the same values but will be shown without finance
THEMES_SECTORS_NO_FINANCE = {
    'artificial intelligence': 11.46,
    'ai': 11.46,
    'marketing': 8.45,
    'risk management': 7.30,
    'machine learning': 6.52,
    'ml': 6.52,
    'business intelligence': 5.85,
    'bi': 5.85,
    'customer service': 2.75,
    'law': 1.82
}

def get_benchmark_value(category: str, report_type: str) -> float:
    """Get ITJobsWatch benchmark value for a category.
    
    Args:
        category: The keyword/category to look up
        report_type: Type of report (languages, cloud, titles, themes, themes_no_finance)
        
    Returns:
        Benchmark percentage or None if not found
    """
    category_lower = category.lower().strip()
    
    benchmarks = {
        'languages': PROGRAMMING_LANGUAGES,
        'cloud': CLOUD_INFRASTRUCTURE,
        'titles': JOB_TITLES,
        'themes': THEMES_SECTORS,
        'themes_no_finance': THEMES_SECTORS_NO_FINANCE
    }
    
    if report_type in benchmarks:
        return benchmarks[report_type].get(category_lower)
    
    return None


def get_report_categories(report_type: str) -> dict:
    """Get all categories and benchmarks for a report type.
    
    Args:
        report_type: Type of report
        
    Returns:
        Dictionary of categories and their benchmark values
    """
    benchmarks = {
        'languages': PROGRAMMING_LANGUAGES,
        'cloud': CLOUD_INFRASTRUCTURE,
        'titles': JOB_TITLES,
        'themes': THEMES_SECTORS,
        'themes_no_finance': THEMES_SECTORS_NO_FINANCE
    }
    
    return benchmarks.get(report_type, {})