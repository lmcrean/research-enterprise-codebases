"""Normalized (percentage-based) stacked bar chart generator."""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional


def get_distinct_colors(n: int) -> List[str]:
    """Generate distinct colors for stacked bars."""
    base_colors = [
        '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
        '#FF8C00', '#8B008B', '#00CED1', '#FFD700', '#32CD32', '#FF69B4',
        '#4B0082', '#FA8072', '#20B2AA', '#9370DB', '#FF6347', '#3CB371',
        '#BA55D3', '#1E90FF', '#FF1493', '#00FA9A', '#DC143C', '#7B68EE',
        '#FF4500', '#2E8B57', '#DAA520', '#800080', '#008080', '#B22222'
    ]
    
    if n <= len(base_colors):
        return base_colors[:n]
    
    import colorsys
    colors = base_colors.copy()
    for i in range(len(base_colors), n):
        hue = (i * 360 / n) % 360
        rgb = colorsys.hsv_to_rgb(hue/360, 0.8, 0.9)
        colors.append('#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        ))
    return colors


def should_use_black_text(color_hex: str) -> bool:
    """Determine if black text should be used based on background color brightness.
    
    Args:
        color_hex: Hex color code (e.g., '#FFFF00')
        
    Returns:
        True if black text should be used, False for white text
    """
    # Remove # if present
    color_hex = color_hex.lstrip('#')
    
    # Convert hex to RGB
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    
    # Calculate luminance using relative luminance formula
    # https://en.wikipedia.org/wiki/Relative_luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Use black text for bright colors (luminance > 0.5)
    # Also specifically check for known light colors
    light_colors = ['#FFFF00', '#00FF00', '#00FFFF', '#FFD700', '#32CD32', 
                    '#00FA9A', '#FA8072', '#20B2AA', '#FF69B4']
    
    return luminance > 0.5 or color_hex.upper() in [c.lstrip('#') for c in light_colors]


def create_normalized_stacked_chart(
    data: Dict[str, Dict[str, int]],
    title: str,
    output_path: str,
    categories_order: Optional[List[str]] = None
) -> None:
    """Create normalized stacked bar chart with percentages and count labels.
    
    Args:
        data: Dictionary {board_name: {keyword: count}}
        title: Chart title
        output_path: Path to save the PNG file
        categories_order: Optional list of categories in display order
    """
    boards = list(data.keys())
    
    # Get categories
    if categories_order:
        categories = categories_order
    else:
        all_categories = set()
        for board_data in data.values():
            all_categories.update(board_data.keys())
        totals = {}
        for cat in all_categories:
            totals[cat] = sum(data[board].get(cat, 0) for board in boards)
        categories = sorted(all_categories, key=lambda x: totals[x], reverse=True)
    
    # Prepare data
    n_boards = len(boards)
    n_categories = len(categories)
    
    # Create raw values and percentages
    values = np.zeros((n_categories, n_boards))
    board_totals = []
    
    for j, board in enumerate(boards):
        board_total = sum(data[board].values())
        board_totals.append(board_total)
        for i, cat in enumerate(categories):
            values[i, j] = data[board].get(cat, 0)
    
    # Calculate percentages
    percentages = np.zeros_like(values)
    for j in range(n_boards):
        if board_totals[j] > 0:
            percentages[:, j] = (values[:, j] / board_totals[j]) * 100
    
    # Create figure (16x16 square)
    fig, ax = plt.subplots(figsize=(16, 16))
    
    # Generate colors
    colors = get_distinct_colors(n_categories)
    
    # Create stacked bars
    x = np.arange(n_boards)
    width = 0.6
    
    # Reorder categories for each board (most results at bottom)
    board_categories = []
    for j, board in enumerate(boards):
        # Get categories for this board sorted by count (descending)
        board_cats = [(cat, values[i, j]) for i, cat in enumerate(categories) if values[i, j] > 0]
        board_cats.sort(key=lambda x: x[1], reverse=True)
        board_categories.append([cat for cat, _ in board_cats])
    
    # Plot normalized stacked bars
    bottom = np.zeros(n_boards)
    
    # Track which categories we've added to legend
    legend_added = set()
    legend_handles = []
    legend_labels = []
    
    # For each board, plot its categories in order (largest at bottom)
    max_cats = max(len(cats) for cats in board_categories)
    
    for level in range(max_cats):
        for j, board in enumerate(boards):
            if level < len(board_categories[j]):
                cat = board_categories[j][level]
                cat_idx = categories.index(cat)
                color = colors[cat_idx % len(colors)]
                
                # Create bar
                bar = ax.bar(x[j], percentages[cat_idx, j], width, 
                            bottom=bottom[j], color=color)
                
                # Add to legend if not already added
                if cat not in legend_added:
                    legend_added.add(cat)
                    legend_handles.append(bar[0])
                    legend_labels.append(cat)
                
                # Add count labels inside bars
                count = int(values[cat_idx, j])
                pct = percentages[cat_idx, j]
                if count > 0 and pct > 1.5:  # Only show if >1.5% to avoid clutter
                    y_pos = bottom[j] + pct/2
                    # Show both count and percentage
                    label_text = f'{count}\n({pct:.1f}%)'
                    fontsize = 9 if pct > 3 else 8
                    # Determine text color based on background color
                    text_color = 'black' if should_use_black_text(color) else 'white'
                    ax.text(x[j], y_pos, label_text, 
                           ha='center', va='center', 
                           fontsize=fontsize, fontweight='bold',
                           color=text_color)
                
                bottom[j] += percentages[cat_idx, j]
    
    # Customize chart
    ax.set_xlabel('Job Board', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage of Total Results (%)', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(boards, fontsize=12)
    
    # Set y-axis to 0-100%
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels([f'{y}%' for y in range(0, 101, 10)])
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_axisbelow(True)
    
    # Add total counts below x-axis labels
    for j, board in enumerate(boards):
        ax.text(x[j], -5, f'Total: {board_totals[j]}', 
               ha='center', fontsize=10, fontweight='bold')
    
    # Add legend with custom handles and labels
    if len(legend_labels) <= 15:
        ax.legend(legend_handles, legend_labels, 
                 loc='upper right', bbox_to_anchor=(1.15, 1), 
                 fontsize=10, frameon=False)
    else:
        ncol = min(3, (len(legend_labels) + 9) // 10)
        ax.legend(legend_handles, legend_labels,
                 loc='upper center', bbox_to_anchor=(0.5, -0.08),
                 ncol=ncol, fontsize=9, frameon=False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"Normalized chart saved to: {output_path}")