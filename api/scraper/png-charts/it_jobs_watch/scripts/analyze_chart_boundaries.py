"""Analyze chart boundaries to find exact pixel coordinates."""

import cv2
import numpy as np
from pathlib import Path

# Load the converted PNG
img_path = Path("views/charts/scraped/converted/artificial-intelligence.png")
img = cv2.imread(str(img_path))
height, width = img.shape[:2]

print(f"Image dimensions: {width}x{height}")

# Convert to grayscale for edge detection
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find vertical lines (for x-axis boundaries)
edges = cv2.Canny(gray, 50, 150)
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

# Find leftmost and rightmost vertical lines
vertical_lines = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is mostly vertical
        if abs(x2 - x1) < 5 and abs(y2 - y1) > 50:
            vertical_lines.append(x1)

if vertical_lines:
    chart_left = min(vertical_lines)
    chart_right = max(vertical_lines)
    print(f"Detected chart boundaries: left={chart_left}, right={chart_right}")

# Find horizontal lines (for y-axis boundaries)
horizontal_lines = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is mostly horizontal
        if abs(y2 - y1) < 5 and abs(x2 - x1) > 50:
            horizontal_lines.append(y1)

if horizontal_lines:
    chart_top = min(horizontal_lines)
    chart_bottom = max(horizontal_lines)
    print(f"Detected chart boundaries: top={chart_top}, bottom={chart_bottom}")

# Also check for grid pattern
# The chart has a distinctive grid pattern we can use
# Look for the actual data area by finding where the grid starts/ends

# Create debug image
debug_img = img.copy()
if vertical_lines:
    for x in vertical_lines[:5]:  # Show first 5 vertical lines
        cv2.line(debug_img, (x, 0), (x, height), (0, 255, 0), 1)
if horizontal_lines:
    for y in horizontal_lines[:5]:  # Show first 5 horizontal lines
        cv2.line(debug_img, (0, y), (width, y), (0, 255, 0), 1)

# Save debug image
cv2.imwrite("chart_boundaries_debug.png", debug_img)

# Manual inspection of the chart shows approximate boundaries
print("\nBased on visual inspection:")
print("Chart left edge: ~85-90 pixels (after Y-axis labels)")
print("Chart right edge: ~1280-1290 pixels (before right margin)")
print("Chart top edge: ~105-110 pixels (after title)")
print("Chart bottom edge: ~540-545 pixels (before X-axis labels)")

# Looking at the grid, we can see:
# - X-axis spans from 2005 to 2025 in the labels
# - But the actual data might start earlier (2004) based on manual data
# - Y-axis shows 0% at bottom to 12% at top