"""Visualizer for creating trend charts from ITJobsWatch data."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional
import os

from api.it_jobs_watch.trends.models import TrendCollection


class TrendVisualizer:
    """Creates visualization charts for trend data."""
    
    def __init__(self):
        """Initialize visualizer with style settings."""
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        # Figure settings
        self.figure_size = (14, 8)
        self.dpi = 150
    
    def create_trend_chart(self, collection: TrendCollection, output_path: str, 
                          data_type: str = "job_count"):
        """Create a line chart showing trends for all technologies."""
        # Convert to DataFrame for easier plotting
        df_data = collection.to_dataframe_format()
        df = pd.DataFrame(df_data)
        
        # Filter by data type
        df = df[df['Type'] == data_type]
        
        if df.empty:
            print(f"No data available for type: {data_type}")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Plot each technology
        for technology in collection.get_all_technologies():
            tech_data = df[df['Technology'] == technology].sort_values('Year')
            if not tech_data.empty:
                ax.plot(tech_data['Year'], tech_data['Value'], 
                       marker='o', linewidth=2.5, markersize=6,
                       label=technology)
        
        # Customize chart
        self._customize_chart(ax, data_type)
        
        # Save chart
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved to: {output_path}")
    
    def _customize_chart(self, ax, data_type: str):
        """Apply customizations to the chart."""
        # Title and labels
        title_map = {
            "job_count": "IT Job Market Trends: 20-Year Overview",
            "median_salary": "IT Salary Trends: 20-Year Overview",
            "market_percentage": "IT Market Share Trends: 20-Year Overview"
        }
        
        ylabel_map = {
            "job_count": "Number of Job Postings",
            "median_salary": "Median Salary (£)",
            "market_percentage": "Market Share (%)"
        }
        
        ax.set_title(title_map.get(data_type, "IT Trends"), 
                    fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel("Year", fontsize=14)
        ax.set_ylabel(ylabel_map.get(data_type, "Value"), fontsize=14)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Legend
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
                 borderaxespad=0, frameon=True, fancybox=True)
        
        # Format y-axis
        if data_type == "job_count":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        elif data_type == "median_salary":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{int(x):,}'))
        elif data_type == "market_percentage":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
        
        # X-axis - 20 year range (2005-2024)
        ax.set_xticks(range(2005, 2025, 2))  # Every 2 years to avoid crowding
        ax.set_xlim(2004.5, 2024.5)
        
        # Add source note
        plt.figtext(0.99, 0.01, 'Source: ITJobsWatch.co.uk', 
                   ha='right', va='bottom', fontsize=9, alpha=0.7)