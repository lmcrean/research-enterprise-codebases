"""
Accurate chart parser with proper cropping to avoid cutting into the chart data area.
Based on user feedback that the current cropping is too harsh and creates inaccurate data.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from api.it_jobs_watch.chart_parser import ITJobsWatchChartParser


class AccurateChartParser(ITJobsWatchChartParser):
    """Chart parser with corrected cropping to preserve chart data accuracy."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Corrected chart area coordinates - less aggressive cropping
        # Based on user feedback that current cropping is too harsh
        self.chart_crop = {
            'top_percent': 0.09,    # Minimal top crop (was 0.15)
            'bottom_percent': 0.88, # Minimal bottom crop (was 0.80)
            'left_percent': 0.08,   # Minimal left crop (was 0.12)
            'right_percent': 0.95   # Minimal right crop (was 0.90)
        }
        
        print("Using corrected cropping settings:")
        print(f"  Top: {self.chart_crop['top_percent']*100:.1f}% (was 15%)")
        print(f"  Bottom: {self.chart_crop['bottom_percent']*100:.1f}% (was 80%)")
        print(f"  Left: {self.chart_crop['left_percent']*100:.1f}% (was 12%)")
        print(f"  Right: {self.chart_crop['right_percent']*100:.1f}% (was 90%)")
    
    def extract_chart_area(self, image):
        """Extract chart area with corrected cropping settings."""
        height, width = image.shape[:2]
        
        # Calculate crop coordinates with corrected settings
        top = int(height * self.chart_crop['top_percent'])
        bottom = int(height * self.chart_crop['bottom_percent'])
        left = int(width * self.chart_crop['left_percent'])
        right = int(width * self.chart_crop['right_percent'])
        
        # Extract chart area
        chart_area = image[top:bottom, left:right]
        
        print(f"Chart area extracted with corrected cropping:")
        print(f"  Original image: {image.shape}")
        print(f"  Cropped area: {chart_area.shape}")
        print(f"  Crop coordinates: top={top}, bottom={bottom}, left={left}, right={right}")
        
        return chart_area
    
    def save_debug_images(self, technology, chart_area, orange_mask):
        """Save debug images with corrected cropping indication."""
        debug_dir = os.path.join(self.converted_dir, 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save chart area with corrected cropping
        import cv2
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_corrected_chart_area.png"), chart_area)
        
        # Save orange mask with corrected cropping
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_corrected_orange_mask.png"), orange_mask)
        
        print(f"Corrected debug images saved to {debug_dir}")
        print(f"  - {technology}_corrected_chart_area.png")
        print(f"  - {technology}_corrected_orange_mask.png")
    
    def map_pixels_to_data(self, pixel_points, grid_lines, chart_area, technology):
        """Map pixels to data with grid-aware coordinate system."""
        height, width = chart_area.shape[:2]
        
        # ITJobsWatch charts span 2005-2024 approximately
        year_range = (2005, 2024)
        x_min, x_max = 0, width - 1
        
        # Use detected horizontal grid lines for Y-axis mapping
        horizontal_lines = sorted(grid_lines.get('horizontal', []))
        
        if len(horizontal_lines) >= 2:
            # Use grid lines for accurate percentage mapping
            y_bottom = max(horizontal_lines)  # Bottom line (0%)
            y_top = min(horizontal_lines)     # Top line (12%)
            
            print(f"Using {len(horizontal_lines)} grid lines for Y-axis mapping:")
            print(f"  Bottom (0%): y={y_bottom}")
            print(f"  Top (12%): y={y_top}")
        else:
            # Fallback to chart boundaries
            y_bottom = height - 1
            y_top = 0
            print("Warning: Using chart boundaries for Y-axis (no grid lines detected)")
        
        # Percentage range: 0% to 12% based on the 12 horizontal grid lines
        percent_range = (0.0, 12.0)
        
        data_points = []
        for x, y in pixel_points:
            # Map x to year
            year_ratio = (x - x_min) / (x_max - x_min) if x_max > x_min else 0
            year = year_range[0] + year_ratio * (year_range[1] - year_range[0])
            year = max(year_range[0], min(year_range[1], int(round(year))))
            
            # Map y to percentage using grid-based coordinates
            if y_bottom > y_top:
                percent_ratio = (y_bottom - y) / (y_bottom - y_top)
            else:
                percent_ratio = 0
            
            percentage = percent_range[0] + percent_ratio * (percent_range[1] - percent_range[0])
            percentage = max(0.0, min(12.0, percentage))  # Clamp to valid range
            
            data_points.append((year, percentage))
        
        # Filter and sort
        data_points = [(year, pct) for year, pct in data_points 
                      if year_range[0] <= year <= year_range[1]]
        data_points.sort(key=lambda p: p[0])
        
        print(f"Mapped {len(data_points)} points using corrected coordinates")
        print(f"Y-axis range: {percent_range[0]}% to {percent_range[1]}%")
        
        return data_points