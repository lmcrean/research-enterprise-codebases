"""Stacked bar chart generator for job board data."""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional


def get_distinct_colors(n: int) -> List[str]:
    """Generate distinct colors for stacked bars.
    
    Args:
        n: Number of colors needed
        
    Returns:
        List of hex color codes
    """
    # Define a palette of distinct colors
    base_colors = [
        '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
        '#FF8C00', '#8B008B', '#00CED1', '#FFD700', '#32CD32', '#FF69B4',
        '#4B0082', '#FA8072', '#20B2AA', '#9370DB', '#FF6347', '#3CB371',
        '#BA55D3', '#1E90FF', '#FF1493', '#00FA9A', '#DC143C', '#7B68EE',
        '#FF4500', '#2E8B57', '#DAA520', '#800080', '#008080', '#B22222'
    ]
    
    if n <= len(base_colors):
        return base_colors[:n]
    
    # Generate additional colors if needed
    import colorsys
    colors = base_colors.copy()
    for i in range(len(base_colors), n):
        hue = (i * 360 / n) % 360
        rgb = colorsys.hsv_to_rgb(hue/360, 0.8, 0.9)
        colors.append('#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        ))
    
    return colors


def create_stacked_bar_chart(
    data: Dict[str, Dict[str, int]],
    title: str,
    output_path: str,
    categories_order: Optional[List[str]] = None
) -> None:
    """Create a stacked bar chart for job board data.
    
    Args:
        data: Dictionary {board_name: {keyword: count}}
        title: Chart title
        output_path: Path to save the PNG file
        categories_order: Optional list of categories in display order
    """
    # Get boards and categories
    boards = list(data.keys())
    
    # Get all unique categories
    if categories_order:
        categories = categories_order
    else:
        all_categories = set()
        for board_data in data.values():
            all_categories.update(board_data.keys())
        # Sort by total count
        totals = {}
        for cat in all_categories:
            totals[cat] = sum(data[board].get(cat, 0) for board in boards)
        categories = sorted(all_categories, key=lambda x: totals[x], reverse=True)
    
    # Prepare data matrix
    n_boards = len(boards)
    n_categories = len(categories)
    
    # Create data matrix
    values = np.zeros((n_categories, n_boards))
    for i, cat in enumerate(categories):
        for j, board in enumerate(boards):
            values[i, j] = data[board].get(cat, 0)
    
    # Create figure (16x16 square)
    fig, ax = plt.subplots(figsize=(16, 16))
    
    # Generate colors
    colors = get_distinct_colors(n_categories)
    
    # Create stacked bars
    x = np.arange(n_boards)
    width = 0.6
    
    # Plot stacked bars
    bottom = np.zeros(n_boards)
    for i, cat in enumerate(categories):
        ax.bar(x, values[i], width, bottom=bottom, 
               label=cat, color=colors[i % len(colors)])
        bottom += values[i]
    
    # Customize chart
    ax.set_xlabel('Job Board', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Jobs', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(boards, fontsize=12)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_axisbelow(True)
    
    # Add legend (outside plot area)
    if n_categories <= 15:
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), 
                 fontsize=10, frameon=False)
    else:
        # For many categories, use multiple columns
        ncol = min(3, (n_categories + 9) // 10)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                 ncol=ncol, fontsize=9, frameon=False)
    
    # Add value labels on bars (for major segments only)
    for i, cat in enumerate(categories[:10]):  # Show values for top 10
        for j, board in enumerate(boards):
            val = values[i, j]
            if val > 0:
                y_pos = bottom[j] - values[i, j]/2
                ax.text(x[j], y_pos, f'{int(val)}', 
                       ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"Chart saved to: {output_path}")