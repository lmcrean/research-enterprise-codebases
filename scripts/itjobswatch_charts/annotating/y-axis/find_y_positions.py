"""Find the actual positions of Y-axis percentage markers in the chart."""

import cv2
import numpy as np
from pathlib import Path

# Load the chart
img_path = Path("views/charts/scraped/converted/artificial-intelligence.png")
img = cv2.imread(str(img_path))
height, width = img.shape[:2]

# Focus on the chart area
chart_region = img[105:545, 130:1280]  # The chart area
gray_chart = cv2.cvtColor(chart_region, cv2.COLOR_BGR2GRAY)

# Detect horizontal lines in chart with more sensitive parameters
edges_chart = cv2.Canny(gray_chart, 20, 80)  # Lower thresholds for fainter lines
lines = cv2.HoughLinesP(edges_chart, 1, np.pi/180, 50, minLineLength=400, maxLineGap=20)  # More sensitive detection

horizontal_lines = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is mostly horizontal
        if abs(y2 - y1) < 5 and abs(x2 - x1) > 400:
            # Convert back to full image coordinates
            y_full = y1 + 105  # Add chart_top offset
            horizontal_lines.append(y_full)

# Remove duplicates and sort from bottom to top
horizontal_lines = sorted(list(set(horizontal_lines)))
print(f"Found {len(horizontal_lines)} horizontal grid lines at Y positions:")
for i, y in enumerate(horizontal_lines):
    print(f"  Grid line {i+1}: Y={y}")

# The chart shows 0% at bottom (Y=545) to 12% at top (Y=105)
# So we need to map these Y positions to percentages
chart_bottom = 545
chart_top = 105
chart_height = chart_bottom - chart_top

print(f"\nChart boundaries: top={chart_top}, bottom={chart_bottom}, height={chart_height}")

# Calculate what percentage each horizontal line represents
print(f"\nPercentage mapping:")
for i, y in enumerate(horizontal_lines):
    # Calculate percentage based on position
    pct = 12.0 * (chart_bottom - y) / chart_height
    print(f"  Y={y} -> {pct:.1f}%")

# Create visualization
debug_img = img.copy()

# Mark horizontal grid lines in yellow
for y in horizontal_lines:
    cv2.line(debug_img, (130, y), (1280, y), (0, 255, 255), 1)
    # Add percentage label
    pct = 12.0 * (chart_bottom - y) / chart_height
    cv2.putText(debug_img, f"{pct:.0f}%", (90, y + 5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

cv2.imwrite("y_positions_debug.png", debug_img)
print("\nSaved debug image to y_positions_debug.png")