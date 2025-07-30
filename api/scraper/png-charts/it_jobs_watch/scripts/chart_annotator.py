"""
Chart Annotator for ITJobsWatch data visualization and debugging.
Draws annotations on top of charts to verify coordinate mapping accuracy.
"""

import cv2
import numpy as np
from pathlib import Path
import csv


class ChartAnnotator:
    """Annotates ITJobsWatch charts with grid overlays and data points for visual debugging."""
    
    def __init__(self, chart_path: str):
        """Initialize with path to chart image."""
        self.chart_path = Path(chart_path)
        self.image = cv2.imread(str(self.chart_path))
        if self.image is None:
            raise ValueError(f"Could not load image from {self.chart_path}")
        
        self.height, self.width = self.image.shape[:2]
        
        # Chart boundaries based on actual measurements
        # These match the grid lines visible in the chart
        self.chart_left = 130  # Where the leftmost vertical grid line is
        self.chart_right = 1280  # Where the rightmost vertical grid line is
        self.chart_top = 105  # Where the topmost horizontal grid line is
        self.chart_bottom = 545  # Where the bottommost horizontal grid line is
        
        self.chart_width = self.chart_right - self.chart_left
        self.chart_height = self.chart_bottom - self.chart_top
        
        # Create a copy for annotations
        self.annotated = self.image.copy()
        
    def draw_grid_overlay(self):
        """Draw grid overlay with X-axis (2004-2026) and Y-axis (0-12%)."""
        # X-axis: Match the actual grid lines in the chart
        # These are the exact X positions of the vertical grid lines
        grid_x_positions = [130, 238, 346, 453, 561, 668, 776, 883, 991, 1098, 1206]
        years = list(range(2005, 2026, 2))  # 2005, 2007, 2009, ..., 2025
        
        # Ensure we have the right number of positions
        for i, (year, x) in enumerate(zip(years, grid_x_positions)):
            # Draw vertical line
            cv2.line(self.annotated, (x, self.chart_top), (x, self.chart_bottom), 
                    (200, 200, 200), 1)
            # Draw blue circle at bottom (in the dip)
            cv2.circle(self.annotated, (x, self.chart_bottom), 4, (255, 100, 0), -1)
            # Add year label
            cv2.putText(self.annotated, str(year), (x - 20, self.chart_bottom + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Y-axis: Complete grid coverage for all percentages 0-12%
        # Updated with actual detected 12% line position
        all_y_positions = [545, 509, 472, 435, 399, 362, 325, 289, 252, 215, 179, 142, 87]
        all_percentages = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        for pct, y in zip(all_percentages, all_y_positions):
            # Draw horizontal line
            cv2.line(self.annotated, (self.chart_left, y), (self.chart_right, y),
                    (200, 200, 200), 1)
            # Draw yellow circle at left for Y-axis markers
            cv2.circle(self.annotated, (self.chart_left, y), 4, (0, 255, 255), -1)
            # Draw green circle at right for comparison
            cv2.circle(self.annotated, (self.chart_right, y), 4, (0, 255, 0), -1)
            # Add percentage label
            cv2.putText(self.annotated, f"{pct}%", (self.chart_left - 30, y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    def plot_data_points(self, data_points: list, color=(0, 0, 255), label_offset=(10, -10)):
        """Plot data points on the chart with labels.
        
        Args:
            data_points: List of (year, percentage) tuples
            color: BGR color for points (default: red)
            label_offset: (x, y) offset for labels relative to points
        """
        if not data_points:
            return
        
        # Sort points by year
        sorted_points = sorted(data_points, key=lambda p: p[0])
        
        # Plot points and connect with lines
        prev_point = None
        for year, percentage in sorted_points:
            x = self._year_to_x(year)
            y = self._percentage_to_y(percentage)
            
            # Draw point
            cv2.circle(self.annotated, (x, y), 5, color, -1)
            
            # Add label
            label = f"({year}, {percentage:.1f}%)"
            cv2.putText(self.annotated, label, (x + label_offset[0], y + label_offset[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
            
            # Connect to previous point
            if prev_point:
                cv2.line(self.annotated, prev_point, (x, y), color, 2)
            
            prev_point = (x, y)
    
    def highlight_expected_points(self, expected_points: dict):
        """Highlight expected validation points with special markers.
        
        Args:
            expected_points: Dict of {year: percentage} for expected values
        """
        for year, expected_pct in expected_points.items():
            x = self._year_to_x(year)
            y = self._percentage_to_y(expected_pct)
            
            # Draw crosshair marker
            cv2.line(self.annotated, (x - 10, y), (x + 10, y), (255, 0, 255), 2)
            cv2.line(self.annotated, (x, y - 10), (x, y + 10), (255, 0, 255), 2)
            
            # Add label
            label = f"Expected: {year}={expected_pct}%"
            cv2.putText(self.annotated, label, (x + 15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
    
    def extract_orange_mask(self):
        """Extract mask of orange line from the chart."""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # Define orange color range (adjust if needed)
        lower_orange = np.array([5, 100, 100])
        upper_orange = np.array([25, 255, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_orange, upper_orange)
        
        # Apply morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def save_outputs(self, output_dir: Path, technology: str, data_points: list = None):
        """Save all debug outputs.
        
        Args:
            output_dir: Directory to save outputs
            technology: Technology name for file naming
            data_points: Optional list of (year, percentage) tuples to save as CSV
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save annotated image
        annotated_path = output_dir.parent / f"{technology}_annotated.png"
        cv2.imwrite(str(annotated_path), self.annotated)
        print(f"Saved annotated chart to: {annotated_path}")
        
        # Save grid overlay only
        grid_only = self.image.copy()
        self.annotated = grid_only
        self.draw_grid_overlay()
        grid_path = output_dir / f"{technology}_grid.png"
        cv2.imwrite(str(grid_path), self.annotated)
        print(f"Saved grid overlay to: {grid_path}")
        
        # Save orange mask
        mask = self.extract_orange_mask()
        mask_path = output_dir / f"{technology}_mask.png"
        cv2.imwrite(str(mask_path), mask)
        print(f"Saved orange mask to: {mask_path}")
        
        # Save data points as CSV
        if data_points:
            csv_path = output_dir / f"{technology}_points.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Year', 'Percentage'])
                for year, pct in sorted(data_points, key=lambda p: p[0]):
                    writer.writerow([year, f"{pct:.2f}"])
            print(f"Saved data points to: {csv_path}")
    
    def _year_to_x(self, year: float) -> int:
        """Convert year to x-coordinate."""
        # The actual data spans from 2004 to 2025.5 based on manual data
        # But the visible chart area shows 2005-2025
        min_year = 2005.0  # Chart starts at 2005
        max_year = 2025.0  # Chart ends at 2025
        year_range = max_year - min_year
        year_offset = year - min_year
        x = self.chart_left + int((year_offset / year_range) * self.chart_width)
        return x
    
    def _percentage_to_y(self, percentage: float) -> int:
        """Convert percentage to y-coordinate."""
        # Y-axis is inverted (0% at bottom, 12% at top)
        # Percentages span from 0% to 12%
        pct_range = 12.0
        y = self.chart_bottom - int((percentage / pct_range) * self.chart_height)
        return y


def create_debug_visualization(technology: str, data_points: list, expected_points: dict):
    """Create a complete debug visualization for a technology chart.
    
    Args:
        technology: Technology name (e.g., 'artificial-intelligence')
        data_points: List of (year, percentage) tuples from extraction
        expected_points: Dict of {year: percentage} for expected validation points
    """
    # Paths
    converted_path = Path(f"views/charts/scraped/converted/{technology}.png")
    output_dir = Path("views/charts/drawn-over/debug")
    
    if not converted_path.exists():
        print(f"Error: Converted chart not found at {converted_path}")
        return
    
    # Create annotator
    annotator = ChartAnnotator(str(converted_path))
    
    # Draw grid overlay
    annotator.draw_grid_overlay()
    
    # Plot extracted data points
    if data_points:
        annotator.plot_data_points(data_points, color=(0, 0, 255))  # Red for extracted
    
    # Highlight expected points
    if expected_points:
        annotator.highlight_expected_points(expected_points)
    
    # Save all outputs
    annotator.save_outputs(output_dir, technology, data_points)
    
    print(f"\nDebug visualization complete for {technology}")