"""Find the actual topmost horizontal grid line for 12%."""

import cv2
import numpy as np
from pathlib import Path

# Load the chart
img_path = Path("views/charts/scraped/converted/artificial-intelligence.png")
img = cv2.imread(str(img_path))

# Focus on the very top area of the chart where 12% should be
# Look in the area from Y=70 to Y=140 (above our current chart_top of 105)
top_region = img[70:140, 130:1280]
gray_top = cv2.cvtColor(top_region, cv2.COLOR_BGR2GRAY)

# Use very sensitive detection for faint lines
edges_top = cv2.Canny(gray_top, 10, 50)  # Very low thresholds
lines = cv2.HoughLinesP(edges_top, 1, np.pi/180, 30, minLineLength=200, maxLineGap=30)

top_horizontal_lines = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is mostly horizontal
        if abs(y2 - y1) < 3 and abs(x2 - x1) > 100:
            # Convert back to full image coordinates
            y_full = y1 + 70  # Add offset
            top_horizontal_lines.append(y_full)

# Remove duplicates and sort
top_horizontal_lines = sorted(list(set(top_horizontal_lines)))

print(f"Found {len(top_horizontal_lines)} horizontal lines in top region:")
for i, y in enumerate(top_horizontal_lines):
    print(f"  Line {i+1}: Y={y}")

# Also manually check specific Y positions by looking at pixel intensity
print(f"\nManual inspection of potential 12% line positions:")
test_y_positions = [85, 90, 95, 100, 105, 110]
for y in test_y_positions:
    # Sample a few pixels across the width to see if there's a line pattern
    line_pixels = img[y, 200:1200:100, :]  # Sample every 100 pixels
    # Check if pixels are light gray (grid line color)
    gray_count = 0
    for pixel in line_pixels:
        # Check if pixel is light gray (grid line)
        if all(170 < val < 220 for val in pixel):  # Light gray range
            gray_count += 1
    
    print(f"  Y={y}: {gray_count}/{len(line_pixels)} pixels are light gray")

# Look at the original chart more carefully
print(f"\nLooking at the chart labels on the right:")
# The 12.0% label is visible - let's see what Y position it's at
right_region = img[70:140, 1300:1400]  # Right side where labels are
cv2.imwrite("top_region_debug.png", right_region)

# Create visualization
debug_img = img.copy()
for y in top_horizontal_lines:
    cv2.line(debug_img, (130, y), (1280, y), (0, 0, 255), 2)  # Red lines
    cv2.putText(debug_img, f"Y={y}", (1290, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

# Also mark our current 12% position
current_12_percent = 105
cv2.line(debug_img, (130, current_12_percent), (1280, current_12_percent), (255, 0, 0), 2)  # Blue line
cv2.putText(debug_img, f"Current 12%: Y={current_12_percent}", (150, current_12_percent-10), 
           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

cv2.imwrite("find_top_line_debug.png", debug_img)
print(f"\nSaved debug image to find_top_line_debug.png")