"""
Grid-based chart parser that uses the 12 horizontal grid lines for accurate percentage mapping.
Based on user confirmation that there are 12 light grey horizontal lines representing 0% to 12%.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from api.it_jobs_watch.chart_parser import ITJobsWatchChartParser


class GridBasedChartParser(ITJobsWatchChartParser):
    """Chart parser that uses horizontal grid lines for accurate percentage mapping."""
    
    def map_pixels_to_data(self, pixel_points, grid_lines, chart_area, technology):
        """Map pixel coordinates using grid lines for accurate percentage calculation."""
        height, width = chart_area.shape[:2]
        
        # ITJobsWatch charts span 2005-2024 (approximately)
        year_range = (2005, 2024)
        x_min, x_max = 0, width - 1
        
        # Use the 12 horizontal grid lines for percentage mapping
        # User confirmed: 12 light grey horizontal lines, 0% at bottom, 12% at top
        horizontal_lines = sorted(grid_lines.get('horizontal', []))
        
        if len(horizontal_lines) >= 2:
            # Use detected grid lines for more accurate mapping
            y_bottom = max(horizontal_lines)  # Bottom line (0%)
            y_top = min(horizontal_lines)     # Top line (12%)
            
            print(f"Using grid lines for Y-axis mapping:")
            print(f"  Bottom (0%): y={y_bottom}")
            print(f"  Top (12%): y={y_top}")
            print(f"  Grid lines detected: {len(horizontal_lines)}")
            
            # If we have exactly 13 lines (including 0% and 12%), use them for precise mapping
            if len(horizontal_lines) == 13:
                print("  Perfect grid detection: 13 lines found (0% to 12%)")
            elif len(horizontal_lines) >= 10:
                print(f"  Good grid detection: {len(horizontal_lines)} lines found")
            else:
                print(f"  Partial grid detection: {len(horizontal_lines)} lines found")
        else:
            # Fallback to chart area boundaries
            y_bottom = height - 1
            y_top = 0
            print("Warning: No grid lines detected, using chart area boundaries")
        
        # Always use 0-12% range for artificial intelligence charts
        percent_range = (0.0, 12.0)
        
        data_points = []
        for x, y in pixel_points:
            # Map x to year
            year_ratio = (x - x_min) / (x_max - x_min) if x_max > x_min else 0
            year = year_range[0] + year_ratio * (year_range[1] - year_range[0])
            year = max(year_range[0], min(year_range[1], int(round(year))))
            
            # Map y to percentage using grid line boundaries
            # y_bottom (high pixel value) -> 0%, y_top (low pixel value) -> 12%
            if y_bottom > y_top:
                percent_ratio = (y_bottom - y) / (y_bottom - y_top)
            else:
                percent_ratio = 0
            
            percentage = percent_range[0] + percent_ratio * (percent_range[1] - percent_range[0])
            percentage = max(0.0, min(12.0, percentage))  # Clamp to 0-12%
            
            data_points.append((year, percentage))
        
        # Filter to reasonable year range and sort
        data_points = [(year, pct) for year, pct in data_points 
                      if year_range[0] <= year <= year_range[1]]
        data_points.sort(key=lambda p: p[0])
        
        print(f"Mapped {len(data_points)} pixel points using grid-based coordinate system")
        print(f"Percentage range: {percent_range[0]:.1f}% to {percent_range[1]:.1f}%")
        
        return data_points
    
    def detect_grid_lines(self, chart_area):
        """Enhanced grid line detection focused on horizontal lines for percentage mapping."""
        # Get base grid detection
        grid_lines = super().detect_grid_lines(chart_area)
        
        # Enhance horizontal line detection for percentage mapping
        gray = chart_area[:, :, 0] if len(chart_area.shape) == 3 else chart_area
        
        # Look for light grey horizontal lines more aggressively
        # Use edge detection to find horizontal structures
        horizontal_edges = np.abs(np.diff(gray, axis=0))
        
        # Find rows with strong horizontal structure
        row_strengths = np.mean(horizontal_edges, axis=1)
        
        # Find peaks that might be grid lines
        threshold = np.percentile(row_strengths, 85)  # Top 15% of edge strengths
        potential_lines = []
        
        for i, strength in enumerate(row_strengths):
            if strength > threshold:
                # Check if this forms a horizontal line across most of the width
                row_edges = horizontal_edges[i]
                line_coverage = np.sum(row_edges > threshold * 0.5) / len(row_edges)
                
                if line_coverage > 0.3:  # Line covers at least 30% of width
                    potential_lines.append(i)
        
        # Merge nearby lines and ensure we have reasonable spacing
        merged_lines = []
        min_spacing = chart_area.shape[0] // 20  # Minimum spacing between grid lines
        
        for line_y in potential_lines:
            if not merged_lines or (line_y - merged_lines[-1]) > min_spacing:
                merged_lines.append(line_y)
        
        # Combine with original detection
        all_horizontal = list(set(grid_lines.get('horizontal', []) + merged_lines))
        all_horizontal.sort()
        
        # If we have too many lines, keep the most evenly spaced ones
        if len(all_horizontal) > 15:
            # Keep approximately 12-13 lines that are most evenly spaced
            step = len(all_horizontal) // 12
            all_horizontal = all_horizontal[::step][:13]
        
        enhanced_grid = {
            'horizontal': all_horizontal,
            'vertical': grid_lines.get('vertical', [])
        }
        
        print(f"Enhanced grid detection: {len(enhanced_grid['horizontal'])} horizontal, {len(enhanced_grid['vertical'])} vertical lines")
        
        return enhanced_grid