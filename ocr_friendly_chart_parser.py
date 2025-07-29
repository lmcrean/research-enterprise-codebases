"""
OCR-friendly chart parser with minimal cropping to preserve x and y axis labels.
Based on user feedback that axis labels are needed for accurate OCR coordinate mapping.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.it_jobs_watch.chart_parser import ITJobsWatchChartParser


class OCRFriendlyChartParser(ITJobsWatchChartParser):
    """Chart parser with minimal cropping to preserve axis labels for OCR."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Minimal cropping to preserve axis labels for OCR
        # Only crop the absolute minimum to remove outer margins
        self.chart_crop = {
            'top_percent': 0.03,    # Minimal top crop - preserve title and top labels
            'bottom_percent': 0.97, # Minimal bottom crop - preserve x-axis labels
            'left_percent': 0.02,   # Minimal left crop - preserve y-axis labels
            'right_percent': 0.98   # Minimal right crop - preserve right margin labels
        }
        
        print("Using OCR-friendly cropping settings (preserves axis labels):")
        print(f"  Top: {self.chart_crop['top_percent']*100:.1f}% (minimal, preserve top labels)")
        print(f"  Bottom: {self.chart_crop['bottom_percent']*100:.1f}% (minimal, preserve x-axis)")
        print(f"  Left: {self.chart_crop['left_percent']*100:.1f}% (minimal, preserve y-axis)")
        print(f"  Right: {self.chart_crop['right_percent']*100:.1f}% (minimal, preserve right labels)")
    
    def extract_chart_area(self, image):
        """Extract chart area with OCR-friendly minimal cropping."""
        height, width = image.shape[:2]
        
        # Calculate crop coordinates with minimal cropping
        top = int(height * self.chart_crop['top_percent'])
        bottom = int(height * self.chart_crop['bottom_percent'])
        left = int(width * self.chart_crop['left_percent'])
        right = int(width * self.chart_crop['right_percent'])
        
        # Extract chart area
        chart_area = image[top:bottom, left:right]
        
        print(f"OCR-friendly chart area extracted:")
        print(f"  Original image: {image.shape}")
        print(f"  Chart area: {chart_area.shape}")
        print(f"  Preserved area: {((bottom-top) * (right-left)) / (height * width) * 100:.1f}% of original")
        print(f"  Crop coordinates: top={top}, bottom={bottom}, left={left}, right={right}")
        
        return chart_area
    
    def detect_grid_lines(self, chart_area):
        """Enhanced grid line detection for charts with preserved axis labels."""
        # Call parent method for base detection
        grid_lines = super().detect_grid_lines(chart_area)
        
        height, width = chart_area.shape[:2]
        
        # With minimal cropping, we need to be more careful about detecting
        # actual chart grid lines vs axis labels
        
        # Focus on the inner chart area for grid detection
        # Estimate where the actual plotting area is within the preserved chart
        inner_top = int(height * 0.10)     # Skip title area
        inner_bottom = int(height * 0.85)   # Skip x-axis labels
        inner_left = int(width * 0.08)      # Skip y-axis labels  
        inner_right = int(width * 0.92)     # Skip right margin
        
        inner_chart = chart_area[inner_top:inner_bottom, inner_left:inner_right]
        
        print(f"Analyzing inner chart area for grid lines:")
        print(f"  Inner area: {inner_chart.shape} (within preserved chart)")
        print(f"  Inner bounds: top={inner_top}, bottom={inner_bottom}, left={inner_left}, right={inner_right}")
        
        # Detect horizontal lines in inner area (for percentage grid)
        gray = inner_chart[:, :, 0] if len(inner_chart.shape) == 3 else inner_chart
        
        # Look for horizontal grid lines
        horizontal_gradient = np.abs(np.diff(gray, axis=0))
        row_strengths = np.mean(horizontal_gradient, axis=1)
        
        # Find strong horizontal features
        threshold = np.percentile(row_strengths, 90)
        horizontal_candidates = []
        
        for i, strength in enumerate(row_strengths):
            if strength > threshold:
                # Convert back to full chart coordinates
                full_chart_y = inner_top + i
                horizontal_candidates.append(full_chart_y)
        
        # Remove duplicates and sort
        horizontal_candidates = sorted(list(set(horizontal_candidates)))
        
        # Filter to get evenly spaced grid lines (should be ~12 for 0-12% scale)
        if len(horizontal_candidates) > 5:
            # Keep lines that are reasonably spaced
            filtered_lines = []
            min_spacing = (inner_bottom - inner_top) // 15  # Minimum spacing
            
            for line_y in horizontal_candidates:
                if not filtered_lines or (line_y - filtered_lines[-1]) > min_spacing:
                    filtered_lines.append(line_y)
            
            horizontal_candidates = filtered_lines
        
        # Combine with original detections, preferring inner area detections
        all_horizontal = list(set(grid_lines.get('horizontal', []) + horizontal_candidates))
        all_horizontal.sort()
        
        enhanced_grid = {
            'horizontal': all_horizontal,
            'vertical': grid_lines.get('vertical', [])
        }
        
        print(f"Enhanced grid detection with preserved labels:")
        print(f"  Horizontal lines: {len(enhanced_grid['horizontal'])} (target: ~12 for 0-12% scale)")
        print(f"  Vertical lines: {len(enhanced_grid['vertical'])}")
        
        return enhanced_grid
    
    def save_debug_images(self, technology, chart_area, orange_mask):
        """Save debug images showing OCR-friendly preservation of labels."""
        debug_dir = os.path.join(self.converted_dir, 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save chart area with OCR-friendly cropping
        import cv2
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_ocr_friendly_chart_area.png"), chart_area)
        
        # Save orange mask
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_ocr_friendly_orange_mask.png"), orange_mask)
        
        # Create a version with grid overlay for analysis
        chart_with_grid = chart_area.copy()
        
        # Draw detected grid lines on the image for visual verification
        grid_lines = self.detect_grid_lines(chart_area)
        
        # Draw horizontal grid lines in blue
        for y in grid_lines.get('horizontal', []):
            if 0 <= y < chart_area.shape[0]:
                cv2.line(chart_with_grid, (0, y), (chart_area.shape[1], y), (255, 0, 0), 1)
        
        # Draw vertical grid lines in green  
        for x in grid_lines.get('vertical', []):
            if 0 <= x < chart_area.shape[1]:
                cv2.line(chart_with_grid, (x, 0), (x, chart_area.shape[0]), (0, 255, 0), 1)
        
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_ocr_grid_overlay.png"), chart_with_grid)
        
        print(f"OCR-friendly debug images saved to {debug_dir}:")
        print(f"  - {technology}_ocr_friendly_chart_area.png (preserves axis labels)")
        print(f"  - {technology}_ocr_friendly_orange_mask.png")
        print(f"  - {technology}_ocr_grid_overlay.png (with detected grid lines)")
    
    def map_pixels_to_data(self, pixel_points, grid_lines, chart_area, technology):
        """Map pixels to data using preserved axis labels for coordinate reference."""
        height, width = chart_area.shape[:2]
        
        # With preserved labels, we can be more precise about the coordinate mapping
        # ITJobsWatch charts typically span 2005-2024
        year_range = (2005, 2024)
        
        # Estimate actual plotting area within the preserved chart
        # These are approximate based on typical ITJobsWatch layout
        plot_left = int(width * 0.08)    # After y-axis labels
        plot_right = int(width * 0.92)   # Before right margin
        plot_top = int(height * 0.10)    # After title
        plot_bottom = int(height * 0.85) # Before x-axis labels
        
        print(f"Estimated plotting area within preserved chart:")
        print(f"  Plot bounds: left={plot_left}, right={plot_right}, top={plot_top}, bottom={plot_bottom}")
        print(f"  Plot dimensions: {plot_right-plot_left} x {plot_bottom-plot_top}")
        
        # Use detected horizontal grid lines for Y-axis mapping
        horizontal_lines = sorted(grid_lines.get('horizontal', []))
        
        if len(horizontal_lines) >= 2:
            # Use grid lines within the plotting area
            plot_horizontals = [y for y in horizontal_lines if plot_top <= y <= plot_bottom]
            
            if len(plot_horizontals) >= 2:
                y_bottom = max(plot_horizontals)  # Bottom line (0%)
                y_top = min(plot_horizontals)     # Top line (12%)
                print(f"Using {len(plot_horizontals)} grid lines in plot area:")
                print(f"  Bottom (0%): y={y_bottom}")
                print(f"  Top (12%): y={y_top}")
            else:
                # Fallback to plot boundaries
                y_bottom = plot_bottom
                y_top = plot_top
                print("Using plot boundaries for Y-axis mapping")
        else:
            # Fallback to plot boundaries
            y_bottom = plot_bottom
            y_top = plot_top
            print("No grid lines detected, using plot boundaries")
        
        # Map coordinates
        data_points = []
        for x, y in pixel_points:
            # Map x to year using plot boundaries
            if plot_right > plot_left:
                year_ratio = (x - plot_left) / (plot_right - plot_left)
            else:
                year_ratio = 0
            
            year = year_range[0] + year_ratio * (year_range[1] - year_range[0])
            year = max(year_range[0], min(year_range[1], int(round(year))))
            
            # Map y to percentage (0% to 12% based on 12 horizontal grid lines)
            if y_bottom > y_top:
                percent_ratio = (y_bottom - y) / (y_bottom - y_top)
            else:
                percent_ratio = 0
            
            percentage = 0.0 + percent_ratio * 12.0  # 0% to 12% range
            percentage = max(0.0, min(12.0, percentage))
            
            data_points.append((year, percentage))
        
        # Filter and sort
        data_points = [(year, pct) for year, pct in data_points 
                      if year_range[0] <= year <= year_range[1]]
        data_points.sort(key=lambda p: p[0])
        
        print(f"Mapped {len(data_points)} points using OCR-friendly coordinates")
        
        return data_points