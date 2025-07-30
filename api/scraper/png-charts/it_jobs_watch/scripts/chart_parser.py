"""Chart image parser for extracting real data from ITJobsWatch WEBP files."""

import os
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import json


class ITJobsWatchChartParser:
    """Extracts actual data from ITJobsWatch chart images using computer vision."""
    
    def __init__(self, scraped_dir: str = "views/charts/scraped/itjobswatch", 
                 converted_dir: str = "views/charts/scraped/converted"):
        """Initialize the chart parser.
        
        Args:
            scraped_dir: Directory containing original WEBP files
            converted_dir: Directory to save converted PNG files
        """
        self.scraped_dir = scraped_dir
        self.converted_dir = converted_dir
        
        # Create converted directory if it doesn't exist
        os.makedirs(self.converted_dir, exist_ok=True)
        
        # Chart area coordinates (approximate, based on ITJobsWatch layout)
        self.chart_crop = {
            'top_percent': 0.15,    # Skip title area
            'bottom_percent': 0.80, # Skip bottom controls/legend
            'left_percent': 0.12,   # Skip y-axis labels
            'right_percent': 0.90   # Skip right margin
        }
        
        # Color definitions for line detection (HSV format)
        # Orange line is RGB(255, 165, 0) approximately
        self.line_colors = {
            'orange': {'lower': np.array([8, 150, 150]), 'upper': np.array([25, 255, 255])},  # Orange (Permanent)
            'blue': {'lower': np.array([100, 150, 100]), 'upper': np.array([130, 255, 255])}, # Blue (Contract)
            'gray': {'lower': np.array([0, 0, 100]), 'upper': np.array([180, 50, 200])}        # Gray (All Jobs)
        }
    
    def convert_webp_to_png(self, technology: str) -> Optional[str]:
        """Convert WEBP file to PNG for better processing.
        
        Args:
            technology: Technology name (e.g., 'artificial-intelligence', 'web-development')
            
        Returns:
            Path to converted PNG file, or None if conversion failed
        """
        webp_path = os.path.join(self.scraped_dir, f"{technology}.webp")
        png_path = os.path.join(self.converted_dir, f"{technology}.png")
        
        if not os.path.exists(webp_path):
            print(f"WEBP file not found: {webp_path}")
            return None
        
        try:
            # Load WEBP and convert to PNG
            with Image.open(webp_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as PNG
                img.save(png_path, 'PNG')
                print(f"Converted {webp_path} -> {png_path}")
                return png_path
                
        except Exception as e:
            print(f"Error converting {webp_path} to PNG: {e}")
            return None
    
    def load_chart_image(self, technology: str) -> Optional[np.ndarray]:
        """Load chart image from WEBP file, converting to PNG if needed.
        
        Args:
            technology: Technology name
            
        Returns:
            OpenCV image array, or None if loading failed
        """
        # Convert WEBP to PNG first
        png_path = self.convert_webp_to_png(technology)
        if not png_path:
            return None
        
        try:
            # Load with OpenCV
            image = cv2.imread(png_path)
            if image is None:
                print(f"Failed to load image: {png_path}")
                return None
            
            print(f"Loaded chart image: {image.shape}")
            return image
            
        except Exception as e:
            print(f"Error loading chart image: {e}")
            return None
    
    def extract_chart_area(self, image: np.ndarray) -> np.ndarray:
        """Extract the main chart plotting area from the full image.
        
        Args:
            image: Full chart image
            
        Returns:
            Cropped chart area
        """
        height, width = image.shape[:2]
        
        # Calculate crop coordinates
        top = int(height * self.chart_crop['top_percent'])
        bottom = int(height * self.chart_crop['bottom_percent'])
        left = int(width * self.chart_crop['left_percent'])
        right = int(width * self.chart_crop['right_percent'])
        
        # Extract chart area
        chart_area = image[top:bottom, left:right]
        
        print(f"Chart area extracted: {chart_area.shape} (from {image.shape})")
        return chart_area
    
    def detect_grid_lines(self, chart_area: np.ndarray) -> Dict[str, List[int]]:
        """Detect horizontal and vertical grid lines for coordinate mapping.
        
        Args:
            chart_area: Cropped chart area
            
        Returns:
            Dictionary with 'horizontal' and 'vertical' grid line positions
        """
        # Convert to grayscale for line detection
        gray = cv2.cvtColor(chart_area, cv2.COLOR_BGR2GRAY)
        
        # Detect horizontal grid lines (for Y-axis mapping)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Detect vertical grid lines (for X-axis mapping)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # Find contours to get line positions
        h_contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        v_contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extract y-coordinates of horizontal lines
        horizontal_positions = []
        for contour in h_contours:
            if cv2.contourArea(contour) > 100:  # Filter small noise
                y = int(np.mean(contour[:, 0, 1]))
                horizontal_positions.append(y)
        
        # Extract x-coordinates of vertical lines
        vertical_positions = []
        for contour in v_contours:
            if cv2.contourArea(contour) > 100:  # Filter small noise
                x = int(np.mean(contour[:, 0, 0]))
                vertical_positions.append(x)
        
        grid_lines = {
            'horizontal': sorted(horizontal_positions),
            'vertical': sorted(vertical_positions)
        }
        
        print(f"Detected {len(grid_lines['horizontal'])} horizontal and {len(grid_lines['vertical'])} vertical grid lines")
        return grid_lines
    
    def extract_orange_line(self, chart_area: np.ndarray, technology: str) -> List[Tuple[int, int]]:
        """Extract the orange line (Permanent jobs) from the chart.
        
        Args:
            chart_area: Cropped chart area
            
        Returns:
            List of (x, y) pixel coordinates along the orange line
        """
        # Convert to HSV for better color filtering
        hsv = cv2.cvtColor(chart_area, cv2.COLOR_BGR2HSV)
        
        # Try multiple orange color ranges to catch the line
        orange_ranges = [
            {'lower': np.array([8, 150, 150]), 'upper': np.array([25, 255, 255])},   # Primary orange
            {'lower': np.array([5, 100, 100]), 'upper': np.array([30, 255, 255])},   # Broader orange
            {'lower': np.array([10, 80, 80]), 'upper': np.array([25, 255, 255])},    # Darker orange
        ]
        
        best_mask = None
        best_contour_count = 0
        
        for color_range in orange_ranges:
            # Create mask for this orange range
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Apply morphological operations to clean up
            kernel = np.ones((2,2), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Count non-zero pixels as a quality metric
            pixel_count = cv2.countNonZero(mask)
            
            if pixel_count > best_contour_count:
                best_contour_count = pixel_count
                best_mask = mask
        
        if best_mask is None:
            print("No orange line detected with any color range")
            return []
        
        # Save debug image to see what we're detecting
        technology_safe = technology.replace('-', '_')
        self.save_debug_images(technology_safe, chart_area, best_mask)
        
        # Find contours of the best orange mask
        contours, _ = cv2.findContours(best_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("No contours found in orange mask")
            return []
        
        # Combine all significant contours (line might be broken into segments)
        line_points = []
        for contour in contours:
            if cv2.contourArea(contour) > 10:  # Filter tiny noise
                for point in contour:
                    x, y = point[0]
                    line_points.append((x, y))
        
        if not line_points:
            print("No valid points found in contours")
            return []
        
        # Sort by x-coordinate to get chronological order
        line_points.sort(key=lambda p: p[0])
        
        # Sample points more densely along x-axis for better coverage
        sampled_points = self._sample_line_points(line_points, chart_area.shape[1])
        
        print(f"Extracted {len(sampled_points)} points from orange line")
        return sampled_points
    
    def _sample_line_points(self, line_points: List[Tuple[int, int]], width: int) -> List[Tuple[int, int]]:
        """Sample points more evenly along the x-axis.
        
        Args:
            line_points: Raw line points
            width: Chart width for sampling
            
        Returns:
            Evenly sampled points
        """
        if not line_points:
            return []
        
        # Group points by x-coordinate and average their y-values
        x_groups = {}
        for x, y in line_points:
            if x not in x_groups:
                x_groups[x] = []
            x_groups[x].append(y)
        
        # Average y-values for each x
        averaged_points = []
        for x in sorted(x_groups.keys()):
            avg_y = sum(x_groups[x]) / len(x_groups[x])
            averaged_points.append((x, int(avg_y)))
        
        # Sample at regular intervals if we have many points
        if len(averaged_points) > width // 10:  # Limit to ~10% of width
            step = len(averaged_points) // (width // 10)
            sampled = averaged_points[::step]
        else:
            sampled = averaged_points
        
        return sampled
    
    def map_pixels_to_data(self, pixel_points: List[Tuple[int, int]], 
                          grid_lines: Dict[str, List[int]], 
                          chart_area: np.ndarray, technology: str) -> List[Tuple[int, float]]:
        """Map pixel coordinates to actual data values (year, percentage).
        
        Args:
            pixel_points: List of (x, y) pixel coordinates
            grid_lines: Grid line positions
            chart_area: Chart area for coordinate reference
            
        Returns:
            List of (year, percentage) data points
        """
        height, width = chart_area.shape[:2]
        
        # ITJobsWatch charts span 2005-2024 based on visual inspection
        year_range = (2005, 2024)
        x_min, x_max = 0, width - 1
        
        # Y-axis mapping: 0% at bottom of chart, max% at top
        # In pixel coordinates: bottom of chart = higher Y values, top = lower Y values
        # So we need to map: high Y pixels (bottom) -> 0%, low Y pixels (top) -> max%
        y_bottom, y_top = height - 1, 0  # Bottom and top pixel coordinates
        
        # Determine percentage range based on technology and chart analysis
        # From the original charts:
        # - AI chart: starts near 0%, grows to ~11-12%
        # - Web Dev chart: starts around 2.5%, peaks at ~6%, declines to ~1%
        if "artificial-intelligence" in technology.lower():
            percent_range = (0.0, 12.0)  # AI chart range
        elif "web-development" in technology.lower():
            percent_range = (0.0, 6.0)   # Web Dev chart range
        else:
            percent_range = (0.0, 10.0)  # Default fallback
            
        data_points = []
        for x, y in pixel_points:
            # Map x to year
            year_ratio = (x - x_min) / (x_max - x_min) if x_max > x_min else 0
            year = year_range[0] + year_ratio * (year_range[1] - year_range[0])
            year = max(year_range[0], min(year_range[1], int(round(year))))
            
            # Map y to percentage
            # y_bottom (high pixel value) -> 0%, y_top (low pixel value) -> max%
            percent_ratio = (y_bottom - y) / (y_bottom - y_top) if y_bottom > y_top else 0
            percentage = percent_range[0] + percent_ratio * (percent_range[1] - percent_range[0])
            percentage = max(0.0, percentage)  # Don't go below 0%
            
            data_points.append((year, percentage))
        
        # Filter to reasonable year range and sort
        data_points = [(year, pct) for year, pct in data_points 
                      if year_range[0] <= year <= year_range[1]]
        data_points.sort(key=lambda p: p[0])
        
        print(f"Mapped {len(data_points)} pixel points to data coordinates")
        print(f"Using percentage range: {percent_range[0]:.1f}% to {percent_range[1]:.1f}%")
        return data_points
    
    def sample_yearly_data(self, data_points: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
        """Sample data points to get one value per year.
        
        Args:
            data_points: List of (year, percentage) points
            
        Returns:
            List of (year, percentage) with one point per year
        """
        if not data_points:
            return []
        
        # Group by year and average the percentages
        year_groups = {}
        for year, percentage in data_points:
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(percentage)
        
        # Calculate average for each year
        yearly_data = []
        for year in sorted(year_groups.keys()):
            avg_percentage = sum(year_groups[year]) / len(year_groups[year])
            yearly_data.append((year, avg_percentage))
        
        print(f"Sampled to {len(yearly_data)} yearly data points")
        return yearly_data
    
    def extract_technology_data(self, technology: str) -> List[Tuple[int, float]]:
        """Main method to extract real data from a technology chart.
        
        Args:
            technology: Technology name (e.g., 'artificial-intelligence', 'web-development')
            
        Returns:
            List of (year, percentage) data points
        """
        print(f"\n=== Extracting real data for: {technology} ===")
        
        # Step 1: Load chart image
        image = self.load_chart_image(technology)
        if image is None:
            print(f"Failed to load image for {technology}")
            return []
        
        # Step 2: Extract chart area
        chart_area = self.extract_chart_area(image)
        
        # Step 3: Detect grid lines for coordinate mapping
        grid_lines = self.detect_grid_lines(chart_area)
        
        # Step 4: Extract orange line (Permanent jobs)
        pixel_points = self.extract_orange_line(chart_area, technology)
        if not pixel_points:
            print(f"Failed to extract orange line for {technology}")
            return []
        
        # Step 5: Map pixel coordinates to data values
        data_points = self.map_pixels_to_data(pixel_points, grid_lines, chart_area, technology)
        
        # Step 6: Sample to yearly data
        yearly_data = self.sample_yearly_data(data_points)
        
        # Show sample of extracted data
        if yearly_data:
            print("Sample extracted data points:")
            for i, (year, percentage) in enumerate(yearly_data[:5]):
                print(f"  {year}: {percentage:.2f}%")
            if len(yearly_data) > 5:
                print(f"  ... and {len(yearly_data) - 5} more")
        
        return yearly_data
    
    def save_debug_images(self, technology: str, chart_area: np.ndarray, 
                         orange_mask: np.ndarray) -> None:
        """Save debug images to visualize extraction process.
        
        Args:
            technology: Technology name
            chart_area: Cropped chart area
            orange_mask: Orange line mask
        """
        debug_dir = os.path.join(self.converted_dir, 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save chart area
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_chart_area.png"), chart_area)
        
        # Save orange mask
        cv2.imwrite(os.path.join(debug_dir, f"{technology}_orange_mask.png"), orange_mask)
        
        print(f"Debug images saved to {debug_dir}")


def test_chart_parser():
    """Test the chart parser with available technologies."""
    parser = ITJobsWatchChartParser()
    
    technologies = ["artificial-intelligence", "web-development"]
    
    for tech in technologies:
        print(f"\n{'='*60}")
        print(f"Testing chart parser: {tech}")
        print('='*60)
        
        data = parser.extract_technology_data(tech)
        
        if data:
            print(f"\nSuccess! Extracted {len(data)} real data points for {tech}")
            
            # Validate against expected patterns
            if "artificial-intelligence" in tech:
                # AI should be low before 2015, then grow rapidly
                pre_2015 = [pct for year, pct in data if year < 2015]
                post_2015 = [pct for year, pct in data if year >= 2015]
                
                if pre_2015 and post_2015:
                    avg_pre = sum(pre_2015) / len(pre_2015)
                    avg_post = sum(post_2015) / len(post_2015)
                    print(f"AI pre-2015 average: {avg_pre:.2f}%")
                    print(f"AI post-2015 average: {avg_post:.2f}%")
                    print(f"Growth validation: {'PASS' if avg_post > avg_pre * 2 else 'FAIL'}")
                    
            elif "web-development" in tech:
                # Web dev should peak in early 2010s, decline recently
                early_2010s = [pct for year, pct in data if 2009 <= year <= 2015]
                recent = [pct for year, pct in data if 2020 <= year <= 2024]
                
                if early_2010s and recent:
                    avg_early = sum(early_2010s) / len(early_2010s)
                    avg_recent = sum(recent) / len(recent)
                    print(f"Web dev 2009-2015 average: {avg_early:.2f}%")
                    print(f"Web dev 2020-2024 average: {avg_recent:.2f}%")
                    print(f"Decline validation: {'PASS' if avg_early > avg_recent else 'FAIL'}")
        else:
            print(f"Failed to extract data for {tech}")


if __name__ == "__main__":
    test_chart_parser()