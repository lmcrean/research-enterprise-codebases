"""Test grid alignment using manual source of truth data."""

import csv
from pathlib import Path
from chart_annotator import ChartAnnotator

# Read manual source of truth data
manual_data = []
csv_path = Path("views/charts/drawn-over/debug/manual_data_extracted_source_of_truth.csv")
with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2 and row[0].strip() and row[1].strip():
            try:
                year = float(row[0].strip())
                percentage = float(row[1].strip())
                manual_data.append((year, percentage))
            except ValueError:
                continue

print(f"Loaded {len(manual_data)} manual data points")

# Create annotator
annotator = ChartAnnotator("views/charts/scraped/converted/artificial-intelligence.png")

# Draw only the grid overlay first
annotator.draw_grid_overlay()

# Plot manual data points
if manual_data:
    # Filter to show only key points for clarity
    key_years = [2005, 2010, 2015, 2017, 2019, 2020, 2023, 2025]
    key_points = [(y, p) for y, p in manual_data if int(y) in key_years]
    
    print("\nKey manual data points:")
    for year, pct in key_points:
        print(f"  {year:.1f}: {pct:.2f}%")
    
    # Plot all manual data points in green
    annotator.plot_data_points(manual_data, color=(0, 255, 0), label_offset=(5, -5))

# Save test output
output_path = Path("views/charts/drawn-over/debug/alignment_test.png")
import cv2
cv2.imwrite(str(output_path), annotator.annotated)
print(f"\nSaved alignment test to: {output_path}")

# Also check specific coordinate mappings
print("\nCoordinate mapping verification:")
test_years = [2005, 2015, 2017, 2019, 2023, 2025]
for year in test_years:
    x = annotator._year_to_x(year)
    print(f"  Year {year} -> X={x} (chart_left={annotator.chart_left}, chart_right={annotator.chart_right})")

test_percentages = [0, 3, 6, 9, 12]
for pct in test_percentages:
    y = annotator._percentage_to_y(pct)
    print(f"  {pct}% -> Y={y} (chart_top={annotator.chart_top}, chart_bottom={annotator.chart_bottom})")