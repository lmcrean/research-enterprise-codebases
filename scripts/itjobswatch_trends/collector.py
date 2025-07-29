"""Collector for ITJobsWatch historical trend data."""

import time
from typing import List
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.it_jobs_watch.trends.models import TrendCollection, TechnologyTrend
from api.it_jobs_watch.trends.scraper import TrendScraper
from api.it_jobs_watch.trends.parser import TrendParser
from api.it_jobs_watch.trends.calculator import MarketShareCalculator
from api.it_jobs_watch.image_extractor_simple import ITJobsWatchImageExtractor


class TrendCollector:
    """Orchestrates the collection of historical trend data."""
    
    # Technologies to track (focused on accuracy)
    TECHNOLOGIES = [
        "Web Development",
        "Artificial Intelligence"
    ]
    
    def __init__(self):
        """Initialize the collector with image extractor."""
        self.scraper = TrendScraper(delay=2.0)
        self.parser = TrendParser()
        self.image_extractor = ITJobsWatchImageExtractor()
        self.collection = TrendCollection()
    
    def collect_all_trends(self) -> TrendCollection:
        """Collect trend data for all configured technologies."""
        print(f"Starting trend collection for {len(self.TECHNOLOGIES)} technologies...")
        start_time = time.time()
        
        for i, technology in enumerate(self.TECHNOLOGIES):
            print(f"\n[{i+1}/{len(self.TECHNOLOGIES)}] Processing: {technology}")
            
            # Create technology entry
            tech_trend = self.collection.add_technology(
                technology, 
                self.scraper.get_technology_url(technology)
            )
            
            # Extract data from chart images
            data_points = self.image_extractor.extract_technology_data(technology)
            if data_points:
                # Convert to our data model format
                for year, job_count in data_points:
                    tech_trend.add_data_point(year, job_count, "job_count")
                print(f"  [OK] Collected {len(data_points)} data points from image")
            else:
                print(f"  [X] Failed to extract data from image")
        
        elapsed_time = time.time() - start_time
        print(f"\nCollection completed in {elapsed_time:.2f} seconds")
        
        # Generate market share percentages
        print("\nCalculating market share percentages...")
        calculator = MarketShareCalculator(self.collection)
        calculator.generate_market_percentages()
        
        # Validate the data
        if calculator.validate_percentages():
            print("  [OK] Market percentages validated successfully")
        else:
            print("  [!] Warning: Some market percentages may be invalid")
        
        # Additional validation against historical accuracy rules
        print("\nValidating historical accuracy rules...")
        self._validate_historical_accuracy()
        
        # Show summary
        market_summary = calculator.get_market_share_summary()
        print("\nMarket Share Summary (latest year):")
        for tech, yearly_data in market_summary.items():
            if yearly_data:
                latest_year = max(yearly_data.keys())
                latest_percentage = yearly_data[latest_year]
                print(f"  {tech}: {latest_percentage}%")
        
        return self.collection
    
    def _add_demo_data(self, tech_trend: TechnologyTrend):
        """Add demo trend data for visualization purposes."""
        import random
        
        base_values = {
            "Web Development": 8000,
            "Artificial Intelligence": 3000,
            "Software Engineering": 12000,
            "Data Science": 5000,
            "Data Analytics": 4000,
            "Software Development": 10000,
            "IT": 15000
        }
        
        base = base_values.get(tech_trend.technology, 5000)
        
        # Generate 20 years of data (2005-2024)
        for year in range(2005, 2025):
            # Add some randomness and growth trend
            growth_factor = 1 + (year - 2005) * 0.04
            random_factor = random.uniform(0.9, 1.1)
            value = int(base * growth_factor * random_factor)
            
            tech_trend.add_data_point(year, value, "job_count")
        
        print(f"  -> Added demo data ({len(tech_trend.data_points)} points)")
    
    def _validate_historical_accuracy(self):
        """Validate data against known historical accuracy rules."""
        calculator = MarketShareCalculator(self.collection)
        market_summary = calculator.get_market_share_summary()
        
        validation_passed = True
        
        # Rule 1: AI was below 1% market share in 2015 and before
        if "Artificial Intelligence" in market_summary:
            ai_data = market_summary["Artificial Intelligence"]
            pre_2015_violations = []
            for year in range(2005, 2016):
                if year in ai_data and ai_data[year] >= 1.0:
                    pre_2015_violations.append((year, ai_data[year]))
            
            if pre_2015_violations:
                print(f"  [!] AI Rule Violation: Found {len(pre_2015_violations)} years pre-2016 with >=1% market share:")
                for year, percentage in pre_2015_violations:
                    print(f"      {year}: {percentage:.2f}%")
                validation_passed = False
            else:
                print("  [OK] AI Rule: Correctly shows <1% market share pre-2016")
        
        # Rule 2: Web Development fell below 3% market share in 2021-2025
        if "Web Development" in market_summary:
            webdev_data = market_summary["Web Development"]
            recent_high_violations = []
            for year in range(2021, 2025):
                if year in webdev_data and webdev_data[year] >= 3.0:
                    recent_high_violations.append((year, webdev_data[year]))
            
            if recent_high_violations:
                print(f"  [!] Web Dev Rule Violation: Found {len(recent_high_violations)} years 2021-2024 with >=3% market share:")
                for year, percentage in recent_high_violations:
                    print(f"      {year}: {percentage:.2f}%")
                validation_passed = False
            else:
                print("  [OK] Web Dev Rule: Correctly shows <3% market share 2021-2024")
        
        # Rule 3: Web Development was above 3% in 2009-2015
        if "Web Development" in market_summary:
            webdev_data = market_summary["Web Development"]
            early_low_violations = []
            for year in range(2009, 2016):
                if year in webdev_data and webdev_data[year] < 3.0:
                    early_low_violations.append((year, webdev_data[year]))
            
            if early_low_violations:
                print(f"  [!] Web Dev Rule Violation: Found {len(early_low_violations)} years 2009-2015 with <3% market share:")
                for year, percentage in early_low_violations:
                    print(f"      {year}: {percentage:.2f}%")
                validation_passed = False
            else:
                print("  [OK] Web Dev Rule: Correctly shows >3% market share 2009-2015")
        
        if validation_passed:
            print("  [OK] All historical accuracy rules passed!")
        else:
            print("  [!] Some historical accuracy rules failed - data may need adjustment")
    
    def get_collection(self) -> TrendCollection:
        """Get the current trend collection."""
        return self.collection