"""
Structure-based chart parser that detects lines by their geometric structure rather than color.
This approach should be more reliable than color-based detection.
"""

import os
import sys
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ocr_friendly_chart_parser import OCRFriendlyChartParser


class StructureBasedChartParser(OCRFriendlyChartParser):
    """Chart parser that detects grid lines by geometric structure rather than color."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Structure-based chart parser initialized (detects lines by geometry)")
    
    def detect_horizontal_lines(self, chart_area):
        """Detect horizontal lines by analyzing image structure."""
        # Convert to grayscale
        if len(chart_area.shape) == 3:
            gray = cv2.cvtColor(chart_area, cv2.COLOR_BGR2GRAY)
        else:
            gray = chart_area
        
        height, width = gray.shape
        
        # Use edge detection to find horizontal structures
        # Apply horizontal Sobel filter to detect horizontal edges
        sobel_horizontal = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_horizontal = np.abs(sobel_horizontal)
        
        # Find strong horizontal edges
        threshold = np.percentile(sobel_horizontal, 95)  # Top 5% of edge strengths
        strong_edges = sobel_horizontal > threshold
        
        # Analyze each row for horizontal line characteristics
        horizontal_lines = []
        min_line_length = width * 0.4  # Line must span at least 40% of width
        
        for y in range(height):
            row_edges = strong_edges[y, :]
            
            # Count connected horizontal segments
            segments = []
            current_segment = 0
            
            for x in range(width):
                if row_edges[x]:
                    current_segment += 1
                else:
                    if current_segment > 0:
                        segments.append(current_segment)
                        current_segment = 0
            
            # Add final segment if it extends to the end
            if current_segment > 0:
                segments.append(current_segment)
            
            # Check if this row has horizontal line characteristics
            total_line_length = sum(segments)
            
            if total_line_length > min_line_length:
                # Additional check: ensure the line isn't too broken up
                if len(segments) <= 5:  # Not too many gaps
                    horizontal_lines.append(y)
        
        print(f"Structure-based horizontal line detection: {len(horizontal_lines)} candidates")
        
        return horizontal_lines
    
    def detect_vertical_lines(self, chart_area):
        """Detect vertical lines by analyzing image structure."""
        # Convert to grayscale
        if len(chart_area.shape) == 3:
            gray = cv2.cvtColor(chart_area, cv2.COLOR_BGR2GRAY)
        else:
            gray = chart_area
        
        height, width = gray.shape
        
        # Use edge detection to find vertical structures
        # Apply vertical Sobel filter to detect vertical edges
        sobel_vertical = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_vertical = np.abs(sobel_vertical)
        
        # Find strong vertical edges
        threshold = np.percentile(sobel_vertical, 95)  # Top 5% of edge strengths
        strong_edges = sobel_vertical > threshold
        
        # Analyze each column for vertical line characteristics
        vertical_lines = []
        min_line_length = height * 0.3  # Line must span at least 30% of height
        
        for x in range(width):
            col_edges = strong_edges[:, x]
            
            # Count connected vertical segments
            segments = []
            current_segment = 0
            
            for y in range(height):
                if col_edges[y]:
                    current_segment += 1
                else:
                    if current_segment > 0:
                        segments.append(current_segment)
                        current_segment = 0
            
            # Add final segment if it extends to the end
            if current_segment > 0:
                segments.append(current_segment)
            
            # Check if this column has vertical line characteristics
            total_line_length = sum(segments)
            
            if total_line_length > min_line_length:
                # Additional check: ensure the line isn't too broken up
                if len(segments) <= 5:  # Not too many gaps
                    vertical_lines.append(x)
        
        print(f"Structure-based vertical line detection: {len(vertical_lines)} candidates")
        
        return vertical_lines
    
    def filter_grid_lines(self, horizontal_lines, vertical_lines, chart_area):
        """Filter detected lines to find the actual chart grid."""
        height, width = chart_area.shape[:2]
        
        # Filter horizontal lines to find evenly spaced grid
        if len(horizontal_lines) > 3:
            # Estimate chart plotting area
            chart_top = int(height * 0.12)  # Skip title
            chart_bottom = int(height * 0.88)  # Skip x-axis labels
            
            # Filter to chart area
            chart_horizontals = [y for y in horizontal_lines if chart_top <= y <= chart_bottom]
            
            # Find evenly spaced lines (target: 12 for 0-12% grid)
            if len(chart_horizontals) > 12:
                # Calculate spacings and find the most consistent group
                spacings = []
                for i in range(len(chart_horizontals) - 1):
                    spacing = chart_horizontals[i+1] - chart_horizontals[i]
                    spacings.append((spacing, i))
                
                # Find the most common spacing
                spacings.sort()
                median_spacing = spacings[len(spacings)//2][0]
                
                # Keep lines with spacing close to median
                filtered_horizontals = [chart_horizontals[0]]
                for y in chart_horizontals[1:]:
                    if abs((y - filtered_horizontals[-1]) - median_spacing) < median_spacing * 0.5:
                        filtered_horizontals.append(y)
                
                # Limit to ~12 lines for 0-12% scale
                horizontal_lines = filtered_horizontals[:13]
            else:
                horizontal_lines = chart_horizontals
        
        # Filter vertical lines similarly
        if len(vertical_lines) > 3:
            # Estimate chart plotting area
            chart_left = int(width * 0.08)   # Skip y-axis labels
            chart_right = int(width * 0.92)  # Skip right margin
            
            # Filter to chart area
            chart_verticals = [x for x in vertical_lines if chart_left <= x <= chart_right]
            
            # Keep reasonable number of vertical lines (years)
            if len(chart_verticals) > 20:
                # Sample evenly across the range
                step = len(chart_verticals) // 15
                chart_verticals = chart_verticals[::step][:20]
            
            vertical_lines = chart_verticals
        
        print(f"Filtered grid lines:")
        print(f"  Horizontal: {len(horizontal_lines)} lines (target: ~12 for 0-12%)")
        print(f"  Vertical: {len(vertical_lines)} lines")
        
        return horizontal_lines, vertical_lines
    
    def detect_grid_lines(self, chart_area):
        """Detect grid lines using structure-based approach."""
        # Detect lines by geometric structure
        horizontal_lines = self.detect_horizontal_lines(chart_area)
        vertical_lines = self.detect_vertical_lines(chart_area)
        
        # Filter to get actual chart grid
        filtered_horizontal, filtered_vertical = self.filter_grid_lines(
            horizontal_lines, vertical_lines, chart_area
        )
        
        grid_lines = {
            'horizontal': filtered_horizontal,
            'vertical': filtered_vertical
        }
        
        return grid_lines
    
    def save_debug_images(self, technology, chart_area, orange_mask):
        """Save debug images showing structure-based line detection."""
        # Create organized directory structure
        debug_root = os.path.join(self.converted_dir, 'debug')
        masks_dir = os.path.join(debug_root, 'masks')
        data_dir = os.path.join(debug_root, 'data')
        
        os.makedirs(debug_root, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Save basic images
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_chart_area.png"), chart_area)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_orange_mask.png"), orange_mask)
        
        # Create structure analysis images
        gray = cv2.cvtColor(chart_area, cv2.COLOR_BGR2GRAY) if len(chart_area.shape) == 3 else chart_area
        
        # Horizontal edge detection
        sobel_h = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_h_normalized = cv2.normalize(np.abs(sobel_h), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_horizontal_edges.png"), sobel_h_normalized)
        
        # Vertical edge detection
        sobel_v = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3) 
        sobel_v_normalized = cv2.normalize(np.abs(sobel_v), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        cv2.imwrite(os.path.join(masks_dir, f"{technology}_vertical_edges.png"), sobel_v_normalized)
        
        # Create overlay with detected grid lines
        overlay = chart_area.copy()
        grid_lines = self.detect_grid_lines(chart_area)
        
        # Draw detected horizontal lines in red
        for y in grid_lines.get('horizontal', []):
            if 0 <= y < chart_area.shape[0]:
                cv2.line(overlay, (0, y), (chart_area.shape[1], y), (0, 0, 255), 2)
        
        # Draw detected vertical lines in blue
        for x in grid_lines.get('vertical', []):
            if 0 <= x < chart_area.shape[1]:
                cv2.line(overlay, (x, 0), (x, chart_area.shape[0]), (255, 0, 0), 2)
        
        # Overlay orange line in green
        overlay[orange_mask > 0] = [0, 255, 0]
        
        cv2.imwrite(os.path.join(debug_root, f"{technology}_structure_overlay.png"), overlay)
        
        print(f"Structure-based debug output saved:")
        print(f"  debug/masks/:")
        print(f"    - {technology}_chart_area.png")
        print(f"    - {technology}_orange_mask.png")
        print(f"    - {technology}_horizontal_edges.png (edge detection)")
        print(f"    - {technology}_vertical_edges.png (edge detection)")
        print(f"  debug/:")
        print(f"    - {technology}_structure_overlay.png (detected grid lines)")
        print(f"  debug/data/:")
        print(f"    - (JSON files will be saved here by test script)")
        
        return {
            'masks_dir': masks_dir,
            'data_dir': data_dir,
            'debug_root': debug_root
        }