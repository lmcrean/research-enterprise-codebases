"""Find the actual positions of year markers in the chart."""

import cv2
import numpy as np
from pathlib import Path

# Load the chart
img_path = Path("views/charts/scraped/converted/artificial-intelligence.png")
img = cv2.imread(str(img_path))
height, width = img.shape[:2]

# Focus on the X-axis label area (below the chart)
x_axis_region = img[545:600, :]  # Just below the chart bottom

# Convert to grayscale
gray = cv2.cvtColor(x_axis_region, cv2.COLOR_BGR2GRAY)

# Find vertical lines in the bottom area (these are the tick marks)
edges = cv2.Canny(gray, 50, 150)

# Look for vertical lines (tick marks)
tick_positions = []
for x in range(width):
    # Check if there's a vertical line at this position
    column = edges[:, x]
    if np.sum(column) > 20:  # Threshold for detecting a line
        tick_positions.append(x)

# Group nearby positions (within 5 pixels)
grouped_ticks = []
current_group = []
for pos in sorted(tick_positions):
    if not current_group or pos - current_group[-1] <= 5:
        current_group.append(pos)
    else:
        if current_group:
            grouped_ticks.append(int(np.mean(current_group)))
        current_group = [pos]
if current_group:
    grouped_ticks.append(int(np.mean(current_group)))

print(f"Found {len(grouped_ticks)} tick marks at X positions:")
for i, x in enumerate(grouped_ticks):
    print(f"  Tick {i+1}: X={x}")

# Also look at the chart image to find where the grid lines actually are
# by detecting vertical lines in the main chart area
chart_region = img[105:545, :]  # The chart area
gray_chart = cv2.cvtColor(chart_region, cv2.COLOR_BGR2GRAY)

# Detect vertical lines in chart
edges_chart = cv2.Canny(gray_chart, 30, 100)
lines = cv2.HoughLinesP(edges_chart, 1, np.pi/180, 100, minLineLength=300, maxLineGap=10)

vertical_lines = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is mostly vertical
        if abs(x2 - x1) < 5 and abs(y2 - y1) > 200:
            vertical_lines.append(x1)

# Remove duplicates and sort
vertical_lines = sorted(list(set(vertical_lines)))
print(f"\nFound {len(vertical_lines)} vertical grid lines in chart at X positions:")
for i, x in enumerate(vertical_lines[:12]):  # Show first 12
    print(f"  Grid line {i+1}: X={x}")

# Create visualization
debug_img = img.copy()
# Mark tick positions in red
for x in grouped_ticks:
    cv2.line(debug_img, (x, 540), (x, 560), (0, 0, 255), 2)
    
# Mark grid lines in blue
for x in vertical_lines[:12]:
    cv2.line(debug_img, (x, 100), (x, 550), (255, 0, 0), 1)

cv2.imwrite("year_positions_debug.png", debug_img)
print("\nSaved debug image to year_positions_debug.png")