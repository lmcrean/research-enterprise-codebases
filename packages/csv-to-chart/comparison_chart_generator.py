"""Comparison chart generator with ITJobsWatch benchmark column."""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
from normalized_chart_generator import get_distinct_colors, should_use_black_text


def create_comparison_chart(
    job_board_data: Dict[str, Dict[str, int]],
    itjobswatch_data: Dict[str, float],
    title: str,
    output_path: str,
    categories_order: Optional[List[str]] = None
) -> None:
    """Create comparison chart with job boards and ITJobsWatch data.
    
    Args:
        job_board_data: Dictionary {board_name: {keyword: count}}
        itjobswatch_data: Dictionary {keyword: market_share_percentage}
        title: Chart title
        output_path: Path to save the PNG file
        categories_order: Optional list of categories in display order
    """
    # Add ITJobsWatch as a synthetic 4th column
    boards = list(job_board_data.keys()) + ['ITJobsWatch']
    
    # Get categories that exist in both datasets
    if categories_order:
        categories = [c for c in categories_order if c in itjobswatch_data or 
                     any(c in board_data for board_data in job_board_data.values())]
    else:
        all_categories = set()
        for board_data in job_board_data.values():
            all_categories.update(board_data.keys())
        # Add ITJobsWatch categories
        all_categories.update(itjobswatch_data.keys())
        
        # Sort by total presence
        totals = {}
        for cat in all_categories:
            job_board_total = sum(data.get(cat, 0) for data in job_board_data.values())
            itjobs_value = itjobswatch_data.get(cat, 0) * 100  # Scale for comparison
            totals[cat] = job_board_total + itjobs_value
        categories = sorted(all_categories, key=lambda x: totals[x], reverse=True)
    
    # Prepare data
    n_boards = len(boards)
    n_categories = len(categories)
    
    # Create raw values and percentages
    values = np.zeros((n_categories, n_boards))
    board_totals = []
    
    # Process job board data
    for j, board in enumerate(boards[:-1]):  # Exclude ITJobsWatch for now
        board_total = sum(job_board_data[board].values())
        board_totals.append(board_total)
        for i, cat in enumerate(categories):
            values[i, j] = job_board_data[board].get(cat, 0)
    
    # Add ITJobsWatch data - use actual percentages as "counts"
    # This will be normalized to 100% like other columns
    itjobs_total = sum(itjobswatch_data.get(cat, 0) for cat in categories)
    board_totals.append(itjobs_total)
    for i, cat in enumerate(categories):
        if cat in itjobswatch_data:
            values[i, -1] = itjobswatch_data[cat]  # Store original percentage
    
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
    for j in range(n_boards):
        board_cats = [(cat, values[i, j]) for i, cat in enumerate(categories) if values[i, j] > 0]
        board_cats.sort(key=lambda x: x[1], reverse=True)
        board_categories.append([cat for cat, _ in board_cats])
    
    # Plot normalized stacked bars
    bottom = np.zeros(n_boards)
    legend_added = set()
    legend_handles = []
    legend_labels = []
    
    # Plot each level
    max_cats = max(len(cats) for cats in board_categories)
    
    for level in range(max_cats):
        for j, board in enumerate(boards):
            if level < len(board_categories[j]):
                cat = board_categories[j][level]
                cat_idx = categories.index(cat)
                color = colors[cat_idx % len(colors)]
                
                # Create bar
                bar = ax.bar(x[j], percentages[cat_idx, j], width, 
                           bottom=bottom[j], color=color,
                           edgecolor='white', linewidth=0.5)
                
                # Add to legend
                if cat not in legend_added:
                    legend_added.add(cat)
                    legend_handles.append(bar[0])
                    legend_labels.append(cat)
                
                # Add labels
                pct = percentages[cat_idx, j]
                if pct > 1.5:  # Only show if >1.5%
                    y_pos = bottom[j] + pct/2
                    
                    if j < len(boards) - 1:  # Job boards
                        count = int(values[cat_idx, j])
                        label_text = f'{count}\n({pct:.1f}%)'
                    else:  # ITJobsWatch column
                        # Show original market share % and normalized %
                        original_pct = values[cat_idx, j]  # Original ITJobsWatch percentage
                        label_text = f'({original_pct:.1f}%)\n{pct:.1f}%'
                    
                    fontsize = 8 if pct > 3 else 7
                    text_color = 'black' if should_use_black_text(color) else 'white'
                    ax.text(x[j], y_pos, label_text, 
                           ha='center', va='center', 
                           fontsize=fontsize, fontweight='bold',
                           color=text_color)
                
                bottom[j] += percentages[cat_idx, j]
    
    # Customize chart
    ax.set_xlabel('Data Source', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage of Total (%)', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(boards, fontsize=12)
    
    # Highlight ITJobsWatch column
    ax.axvline(x[-1] - width/2 - 0.05, color='red', linestyle='--', alpha=0.3)
    ax.axvline(x[-1] + width/2 + 0.05, color='red', linestyle='--', alpha=0.3)
    
    # Set y-axis to 0-100%
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels([f'{y}%' for y in range(0, 101, 10)])
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_axisbelow(True)
    
    # Add data source notes
    for j, board in enumerate(boards):
        if j < len(boards) - 1:
            ax.text(x[j], -5, f'n={board_totals[j]}', 
                   ha='center', fontsize=10, fontweight='bold')
        else:
            ax.text(x[j], -7, 'ITJobsWatch\n(orig %)\nnorm %', 
                   ha='center', fontsize=9, fontweight='bold', color='red')
    
    # Add legend
    if len(legend_labels) <= 15:
        ax.legend(legend_handles, legend_labels, 
                 loc='upper right', bbox_to_anchor=(1.15, 1), 
                 fontsize=10, frameon=False)
    else:
        ncol = min(3, (len(legend_labels) + 9) // 10)
        ax.legend(legend_handles, legend_labels,
                 loc='upper center', bbox_to_anchor=(0.5, -0.1),
                 ncol=ncol, fontsize=9, frameon=False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"Comparison chart saved to: {output_path}")