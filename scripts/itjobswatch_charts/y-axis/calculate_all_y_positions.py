"""Calculate complete Y positions for all percentage lines 0-12%."""

# Chart boundaries
chart_top = 105    # 12%
chart_bottom = 545  # 0%
chart_height = chart_bottom - chart_top  # 440 pixels

print("Calculating Y positions for all percentages 0-12%:")
print(f"Chart: top={chart_top} (12%), bottom={chart_bottom} (0%), height={chart_height}")

# Calculate Y position for each percentage
all_y_positions = []
all_percentages = []

for pct in range(0, 13):  # 0% to 12%
    # Linear interpolation: 0% is at bottom (Y=545), 12% is at top (Y=105)
    y = chart_bottom - int((pct / 12.0) * chart_height)
    
    all_y_positions.append(y)
    all_percentages.append(pct)
    
    print(f"  {pct}% -> Y={y}")

print(f"\nArray for chart_annotator.py:")
print(f"all_y_positions = {all_y_positions}")
print(f"all_percentages = {all_percentages}")

# Also show the detected lines for comparison
detected_lines = [510, 468, 425, 383, 341, 299, 256, 214, 172, 130]
print(f"\nDetected lines: {detected_lines}")

# Compare calculated vs detected
print(f"\nComparison (calculated vs detected):")
for pct in range(1, 11):  # Skip 0% and 12% as they might not have detected lines
    calc_y = chart_bottom - int((pct / 12.0) * chart_height)
    print(f"  {pct}%: calculated={calc_y}", end="")
    
    # Find closest detected line
    if detected_lines:
        closest = min(detected_lines, key=lambda x: abs(x - calc_y))
        diff = abs(closest - calc_y)
        print(f", closest_detected={closest} (diff={diff})")
    else:
        print()