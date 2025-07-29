"""Exporter for saving trend data to CSV format."""

import pandas as pd
import os
from typing import Optional

from api.it_jobs_watch.trends.models import TrendCollection


class TrendExporter:
    """Exports trend data to various formats."""
    
    def export_to_csv(self, collection: TrendCollection, output_path: str, data_type: str = "job_count"):
        """Export trend data to CSV file."""
        # Convert collection to DataFrame format
        df_data = collection.to_dataframe_format()
        
        if not df_data:
            print("No data to export")
            return
        
        # Create DataFrame
        df = pd.DataFrame(df_data)
        
        # Pivot the data for better readability
        pivot_df = self._create_pivot_table(df, data_type)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        pivot_df.to_csv(output_path, index=True)
        print(f"Data exported to: {output_path}")
        
        # Also save raw format
        raw_path = output_path.replace('.csv', '_raw.csv')
        df.to_csv(raw_path, index=False)
        print(f"Raw data exported to: {raw_path}")
    
    def _create_pivot_table(self, df: pd.DataFrame, data_type: str = "job_count") -> pd.DataFrame:
        """Create a pivot table with years as rows and technologies as columns."""
        # Filter for specified data type
        filtered_data = df[df['Type'] == data_type].copy()
        
        if filtered_data.empty:
            # Fall back to any available data
            filtered_data = df.copy()
        
        # Create pivot table
        pivot = filtered_data.pivot_table(
            index='Year',
            columns='Technology', 
            values='Value',
            aggfunc='mean'  # In case of duplicates
        )
        
        # Sort by year
        pivot = pivot.sort_index()
        
        # Add metadata columns
        pivot.insert(0, 'Data_Type', data_type)
        pivot.insert(1, 'Source', 'ITJobsWatch')
        
        return pivot
    
    def generate_summary_stats(self, collection: TrendCollection) -> pd.DataFrame:
        """Generate summary statistics for the trend data."""
        stats = []
        
        for tech_name, tech_trend in collection.trends.items():
            if not tech_trend.data_points:
                continue
            
            # Get job count data
            job_data = [dp.value for dp in tech_trend.get_data_by_type('job_count')]
            
            if job_data:
                year_range = tech_trend.get_years_range()
                
                stats.append({
                    'Technology': tech_name,
                    'Start_Year': year_range[0],
                    'End_Year': year_range[1],
                    'Data_Points': len(job_data),
                    'Min_Jobs': min(job_data),
                    'Max_Jobs': max(job_data),
                    'Avg_Jobs': sum(job_data) / len(job_data),
                    'Growth_Rate': self._calculate_growth_rate(job_data)
                })
        
        return pd.DataFrame(stats)
    
    def _calculate_growth_rate(self, values: list) -> float:
        """Calculate compound annual growth rate."""
        if len(values) < 2:
            return 0.0
        
        start_value = values[0]
        end_value = values[-1]
        years = len(values) - 1
        
        if start_value <= 0:
            return 0.0
        
        # CAGR formula
        growth_rate = ((end_value / start_value) ** (1 / years) - 1) * 100
        
        return round(growth_rate, 2)