"""
Enhanced OCR-friendly chart parser with light grey mask detection for axis labels.
Includes light_grey_vertical_mask and light_grey_horizontal_mask for accurate grid mapping.
"""

import os
import sys
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ocr_friendly_chart_parser import OCRFriendlyChartParser


class EnhancedOCRChartParser(OCRFriendlyChartParser):
    """Enhanced parser with light grey mask detection for precise grid mapping."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Light grey color range for grid detection (HSV format)
        # ITJobsWatch uses light grey for grid lines - more permissive range
        self.light_grey_range = {
            'lower': np.array([0, 0, 120]),    # Darker grey lower bound (was 150)
            'upper': np.array([180, 50, 250])  # Lighter grey upper bound (was 220)
        }
        
        print("Enhanced OCR parser with light grey mask detection initialized")
    
    def extract_light_grey_horizontal_mask(self, chart_area):
        """Extract horizontal light grey grid lines for percentage mapping."""
        # Convert to HSV for better color filtering
        hsv = cv2.cvtColor(chart_area, cv2.COLOR_BGR2HSV)
        
        # Try multiple grey ranges to capture grid lines
        grey_ranges = [
            {'lower': np.array([0, 0, 100]), 'upper': np.array([180, 60, 255])},   # Very permissive
            {'lower': np.array([0, 0, 120]), 'upper': np.array([180, 50, 250])},   # Current range
            {'lower': np.array([0, 0, 140]), 'upper': np.array([180, 40, 230])},   # Stricter
        ]
        
        best_mask = None
        best_pixel_count = 0
        
        for i, range_def in enumerate(grey_ranges):
            # Create mask for this grey range
            mask = cv2.inRange(hsv, range_def['lower'], range_def['upper'])
            pixel_count = np.sum(mask > 0)
            
            print(f"  Grey range {i+1}: {pixel_count} pixels detected")
            
            if pixel_count > best_pixel_count:
                best_pixel_count = pixel_count
                best_mask = mask
        
        if best_mask is None:
            print("  No grey pixels detected in any range")
            return np.zeros_like(chart_area[:,:,0])
        
        # Focus on horizontal structures only
        # Use morphological operations to isolate horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_mask = cv2.morphologyEx(best_mask, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Clean up the mask
        horizontal_mask = cv2.morphologyEx(horizontal_mask, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))
        
        print(f"Extracted light grey horizontal mask: {np.sum(horizontal_mask > 0)} pixels (after morphology)")
        
        return horizontal_mask
    
    def extract_light_grey_vertical_mask(self, chart_area):
        """Extract vertical light grey grid lines for year mapping."""
        # Convert to HSV for better color filtering
        hsv = cv2.cvtColor(chart_area, cv2.COLOR_BGR2HSV)
        
        # Try multiple grey ranges to capture grid lines
        grey_ranges = [
            {'lower': np.array([0, 0, 100]), 'upper': np.array([180, 60, 255])},   # Very permissive
            {'lower': np.array([0, 0, 120]), 'upper': np.array([180, 50, 250])},   # Current range
            {'lower': np.array([0, 0, 140]), 'upper': np.array([180, 40, 230])},   # Stricter
        ]
        
        best_mask = None
        best_pixel_count = 0
        
        for i, range_def in enumerate(grey_ranges):
            # Create mask for this grey range
            mask = cv2.inRange(hsv, range_def['lower'], range_def['upper'])
            pixel_count = np.sum(mask > 0)
            
            if pixel_count > best_pixel_count:
                best_pixel_count = pixel_count
                best_mask = mask
        
        if best_mask is None:
            return np.zeros_like(chart_area[:,:,0])
        
        # Focus on vertical structures only
        # Use morphological operations to isolate vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        vertical_mask = cv2.morphologyEx(best_mask, cv2.MORPH_OPEN, vertical_kernel)
        
        # Clean up the mask
        vertical_mask = cv2.morphologyEx(vertical_mask, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))
        
        print(f"Extracted light grey vertical mask: {np.sum(vertical_mask > 0)} pixels (after morphology)")
        
        return vertical_mask
    
    def detect_grid_from_masks(self, horizontal_mask, vertical_mask):
        """Detect grid line positions from light grey masks with intelligent filtering."""
        height, width = horizontal_mask.shape
        
        # Find horizontal grid lines with stronger filtering
        horizontal_candidates = []
        for y in range(height):
            row = horizontal_mask[y, :]
            line_coverage = np.sum(row > 0) / width
            
            # Require stronger line coverage for horizontal grid lines
            if line_coverage > 0.6:  # Line covers 60% of width (was 30%)
                horizontal_candidates.append(y)
        
        # Filter horizontal lines to find evenly spaced grid (target: 12 lines for 0-12%)
        if len(horizontal_candidates) > 5:
            # Estimate the chart plotting area (middle 70% typically contains the grid)
            chart_top = int(height * 0.15)
            chart_bottom = int(height * 0.85)
            
            # Filter to lines within the chart area
            chart_horizontals = [y for y in horizontal_candidates if chart_top <= y <= chart_bottom]
            
            # If we have too many lines, keep the most evenly spaced ones
            if len(chart_horizontals) > 15:
                # Calculate average spacing and keep lines close to that spacing
                if len(chart_horizontals) > 1:
                    spacings = [chart_horizontals[i+1] - chart_horizontals[i] 
                               for i in range(len(chart_horizontals)-1)]
                    avg_spacing = np.median(spacings)
                    
                    # Keep lines that maintain reasonable spacing
                    filtered_horizontals = [chart_horizontals[0]]
                    for line_y in chart_horizontals[1:]:
                        if (line_y - filtered_horizontals[-1]) >= (avg_spacing * 0.7):
                            filtered_horizontals.append(line_y)
                    
                    chart_horizontals = filtered_horizontals[:13]  # Limit to ~12 grid lines
            
            horizontal_positions = chart_horizontals
        else:
            horizontal_positions = horizontal_candidates
        
        # Find vertical grid lines with similar filtering
        vertical_candidates = []
        for x in range(width):
            col = vertical_mask[:, x]
            line_coverage = np.sum(col > 0) / height
            
            # Require good line coverage for vertical grid lines
            if line_coverage > 0.4:  # Line covers 40% of height
                vertical_candidates.append(x)
        
        # Filter vertical lines to reasonable chart boundaries
        if len(vertical_candidates) > 3:
            # Estimate chart left/right boundaries
            chart_left = int(width * 0.1)
            chart_right = int(width * 0.9)
            
            chart_verticals = [x for x in vertical_candidates if chart_left <= x <= chart_right]
            
            # Limit to reasonable number of vertical lines
            if len(chart_verticals) > 20:
                # Keep evenly spaced lines
                step = len(chart_verticals) // 15
                chart_verticals = chart_verticals[::step][:20]
            
            vertical_positions = chart_verticals
        else:
            vertical_positions = vertical_candidates
        
        grid_lines = {
            'horizontal': horizontal_positions,
            'vertical': vertical_positions
        }
        
        print(f"Grid lines detected from light grey masks (filtered):")
        print(f"  Horizontal: {len(grid_lines['horizontal'])} lines (target: ~12)")
        print(f"  Vertical: {len(grid_lines['vertical'])} lines")
        
        return grid_lines
    
    def detect_grid_lines(self, chart_area):
        """Enhanced grid detection using light grey masks."""
        # Extract light grey masks
        horizontal_mask = self.extract_light_grey_horizontal_mask(chart_area)
        vertical_mask = self.extract_light_grey_vertical_mask(chart_area)
        
        # Detect grid lines from masks
        mask_grid = self.detect_grid_from_masks(horizontal_mask, vertical_mask)
        
        # Combine with parent detection for robustness
        parent_grid = super().detect_grid_lines(chart_area)
        
        # Merge results, preferring mask-based detection
        all_horizontal = list(set(mask_grid.get('horizontal', []) + parent_grid.get('horizontal', [])))
        all_vertical = list(set(mask_grid.get('vertical', []) + parent_grid.get('vertical', [])))
        
        combined_grid = {
            'horizontal': sorted(all_horizontal),
            'vertical': sorted(all_vertical)
        }
        
        print(f"Combined grid detection results:")
        print(f"  Horizontal: {len(combined_grid['horizontal'])} lines (target: 12 for 0-12%)")
        print(f"  Vertical: {len(combined_grid['vertical'])} lines")
        
        return combined_grid
    
    def save_debug_images(self, technology, chart_area, orange_mask):
        """Save debug images with organized directory structure."""
        # Create organized directory structure
        debug_root = os.path.join(self.converted_dir, 'debug')
        masks_dir = os.path.join(debug_root, 'masks')
        data_dir = os.path.join(debug_root, 'data')
        
        os.makedirs(debug_root, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Save basic debug images to masks directory
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_chart_area.png"), chart_area)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_orange_mask.png"), orange_mask)
        
        # Extract and save light grey masks
        horizontal_mask = self.extract_light_grey_horizontal_mask(chart_area)
        vertical_mask = self.extract_light_grey_vertical_mask(chart_area)
        
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_light_grey_horizontal_mask.png"), horizontal_mask)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_light_grey_vertical_mask.png"), vertical_mask)
        
        # Create combined mask visualization
        combined_mask = cv2.bitwise_or(horizontal_mask, vertical_mask)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_light_grey_combined_mask.png"), combined_mask)
        
        # Create overlay showing all detected elements
        overlay = chart_area.copy()
        
        # Overlay horizontal mask in red
        overlay[horizontal_mask > 0] = [0, 0, 255]
        
        # Overlay vertical mask in blue
        overlay[vertical_mask > 0] = [255, 0, 0]
        
        # Overlay orange line in green
        overlay[orange_mask > 0] = [0, 255, 0]
        
        cv2.imwrite(os.path.join(debug_root, f"{technology}_enhanced_overlay.png"), overlay)
        
        print(f"Organized debug output saved:")
        print(f"  debug/masks/:")
        print(f"    - {technology}_chart_area.png")
        print(f"    - {technology}_orange_mask.png")
        print(f"    - {technology}_light_grey_horizontal_mask.png")
        print(f"    - {technology}_light_grey_vertical_mask.png")
        print(f"    - {technology}_light_grey_combined_mask.png")
        print(f"  debug/:")
        print(f"    - {technology}_enhanced_overlay.png (all elements combined)")
        print(f"  debug/data/:")
        print(f"    - (JSON files will be saved here by test script)")
        
        return {
            'masks_dir': masks_dir,
            'data_dir': data_dir,
            'debug_root': debug_root
        }
    
    def map_pixels_to_data(self, pixel_points, grid_lines, chart_area, technology):
        """Enhanced pixel mapping using light grey grid detection."""
        height, width = chart_area.shape[:2]
        
        # ITJobsWatch charts span 2005-2024
        year_range = (2005, 2024)
        
        # Use detected grid lines for more accurate mapping
        horizontal_lines = sorted(grid_lines.get('horizontal', []))
        vertical_lines = sorted(grid_lines.get('vertical', []))
        
        print(f"Enhanced coordinate mapping:")
        print(f"  Chart dimensions: {width} x {height}")
        print(f"  Available horizontal grid lines: {len(horizontal_lines)}")
        print(f"  Available vertical grid lines: {len(vertical_lines)}")
        
        # Determine plotting area using grid lines
        if len(horizontal_lines) >= 2:
            y_top = min(horizontal_lines)      # Top (12%)
            y_bottom = max(horizontal_lines)   # Bottom (0%)
            print(f"  Y-axis from grid: {y_top} (12%) to {y_bottom} (0%)")
        else:
            # Fallback to estimated plot area
            y_top = int(height * 0.10)
            y_bottom = int(height * 0.85)
            print(f"  Y-axis estimated: {y_top} to {y_bottom}")
        
        if len(vertical_lines) >= 2:
            x_left = min(vertical_lines)       # Left (2005)
            x_right = max(vertical_lines)      # Right (2024)
            print(f"  X-axis from grid: {x_left} (2005) to {x_right} (2024)")
        else:
            # Fallback to estimated plot area
            x_left = int(width * 0.08)
            x_right = int(width * 0.92)
            print(f"  X-axis estimated: {x_left} to {x_right}")
        
        # Map pixel coordinates to data values
        data_points = []
        for x, y in pixel_points:
            # Map x to year
            if x_right > x_left:
                year_ratio = (x - x_left) / (x_right - x_left)
            else:
                year_ratio = 0
            
            year = year_range[0] + year_ratio * (year_range[1] - year_range[0])
            year = max(year_range[0], min(year_range[1], int(round(year))))
            
            # Map y to percentage (0% to 12%)
            if y_bottom > y_top:
                percent_ratio = (y_bottom - y) / (y_bottom - y_top)
            else:
                percent_ratio = 0
            
            percentage = 0.0 + percent_ratio * 12.0
            percentage = max(0.0, min(12.0, percentage))
            
            data_points.append((year, percentage))
        
        # Filter and sort
        data_points = [(year, pct) for year, pct in data_points 
                      if year_range[0] <= year <= year_range[1]]
        data_points.sort(key=lambda p: p[0])
        
        print(f"Enhanced mapping completed: {len(data_points)} points")
        
        return data_points