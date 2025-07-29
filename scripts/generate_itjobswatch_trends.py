"""Main script to generate ITJobsWatch 10-year trend charts and data."""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.itjobswatch_trends.collector import TrendCollector
from scripts.itjobswatch_trends.visualizer import TrendVisualizer
from scripts.itjobswatch_trends.exporter import TrendExporter


def main():
    """Main function to orchestrate trend data collection and visualization."""
    print("=" * 60)
    print("ITJobsWatch 20-Year Trend Analysis")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize components
    collector = TrendCollector()
    visualizer = TrendVisualizer()
    exporter = TrendExporter()
    
    # Define output paths
    chart_path = os.path.join('views', 'charts', 'itjobswatch_20year_trends.png')
    csv_path = os.path.join('views', 'tables', 'itjobswatch_20year_trends.csv')
    
    # Market share percentage chart
    market_chart_path = os.path.join('views', 'charts', 'itjobswatch_20year_market_share.png')
    market_csv_path = os.path.join('views', 'tables', 'itjobswatch_20year_market_share.csv')
    
    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Step 1: Collect data
    print("Step 1: Collecting trend data...")
    collection = collector.collect_all_trends()
    
    # Step 2: Generate visualizations
    print("\nStep 2: Creating trend charts...")
    visualizer.create_trend_chart(collection, chart_path, data_type="job_count")
    print("  [OK] Absolute numbers chart created")
    
    visualizer.create_trend_chart(collection, market_chart_path, data_type="market_percentage")
    print("  [OK] Market share percentage chart created")
    
    # Step 3: Export data
    print("\nStep 3: Exporting data to CSV...")
    exporter.export_to_csv(collection, csv_path)
    print("  [OK] Raw data exported")
    
    exporter.export_to_csv(collection, market_csv_path, data_type="market_percentage")
    print("  [OK] Market share data exported")
    
    # Step 4: Generate summary statistics
    print("\nStep 4: Generating summary statistics...")
    summary_df = exporter.generate_summary_stats(collection)
    
    if not summary_df.empty:
        print("\nSummary Statistics:")
        print(summary_df.to_string(index=False))
        
        # Save summary
        summary_path = csv_path.replace('.csv', '_summary.csv')
        summary_df.to_csv(summary_path, index=False)
        print(f"\nSummary saved to: {summary_path}")
    
    print("\n" + "=" * 60)
    print("Analysis completed successfully!")
    print(f"Absolute numbers chart: {chart_path}")
    print(f"Market share chart: {market_chart_path}")
    print(f"Raw data: {csv_path}")
    print(f"Market share data: {market_csv_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()