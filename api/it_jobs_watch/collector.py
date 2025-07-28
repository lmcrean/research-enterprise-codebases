"""Data collection orchestrator for IT Jobs Watch statistics."""

import csv
import json
import time
import os
import sys
from typing import List, Dict

# Add parent directory to path for imports when run standalone
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from .client import ITJobsWatchClient
    from .models import JobMarketStats, JobMarketMetadata
except ImportError:
    # Fallback for standalone execution
    from client import ITJobsWatchClient
    from models import JobMarketStats, JobMarketMetadata


class ITJobsWatchCollector:
    """Orchestrates collection of job market data from IT Jobs Watch."""
    
    def __init__(self, technologies: List[str], output_dir: str = "data/raw"):
        """Initialize collector with list of technologies to track."""
        self.technologies = technologies
        self.output_dir = output_dir
        self.client = ITJobsWatchClient()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def collect_all_data(self) -> Dict:
        """Collect job market data for all configured technologies."""
        print("Starting IT Jobs Watch data collection...")
        start_time = time.time()
        
        all_stats = []
        
        for i, technology in enumerate(self.technologies, 1):
            print(f"Collecting data for {technology} ({i}/{len(self.technologies)})")
            
            tech_stats = self.client.get_london_job_stats(technology)
            all_stats.extend(tech_stats)
            
            print(f"   Found {len(tech_stats)} job roles for {technology}")
        
        # Save data to CSV
        csv_path = os.path.join(self.output_dir, "itjobswatch_stats.csv")
        self._save_to_csv(all_stats, csv_path)
        
        # Create and save metadata
        collection_time = time.time() - start_time
        metadata = JobMarketMetadata.create(
            tech_count=len(self.technologies),
            location="London",
            collection_time=collection_time
        )
        
        metadata_path = os.path.join(self.output_dir, "itjobswatch_metadata.json")
        self._save_metadata(metadata, metadata_path)
        
        summary = {
            'total_job_roles': len(all_stats),
            'technologies_searched': len(self.technologies),
            'collection_time_seconds': round(collection_time, 2),
            'csv_file': csv_path,
            'metadata_file': metadata_path
        }
        
        print(f"Collection complete! Found {len(all_stats)} job roles in {collection_time:.1f}s")
        return summary
    
    def _save_to_csv(self, stats: List[JobMarketStats], file_path: str):
        """Save job market statistics to CSV file."""
        if not stats:
            print("No data to save")
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = stats[0].to_dict().keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for stat in stats:
                writer.writerow(stat.to_dict())
        
        print(f"Saved {len(stats)} records to {file_path}")
    
    def _save_metadata(self, metadata: JobMarketMetadata, file_path: str):
        """Save collection metadata to JSON file."""
        metadata_dict = {
            'last_updated': metadata.last_updated,
            'total_technologies': metadata.total_technologies,
            'location': metadata.location,
            'collection_time_seconds': metadata.collection_time_seconds
        }
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata_dict, jsonfile, indent=2)
        
        print(f"Saved metadata to {file_path}")


def main():
    """Main function for standalone execution."""
    technologies = [
        "C#",
        "Python", 
        "TypeScript",
        "Software Engineering",
        "Artificial Intelligence"
    ]
    
    collector = ITJobsWatchCollector(technologies)
    summary = collector.collect_all_data()
    
    print("\nCollection Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()