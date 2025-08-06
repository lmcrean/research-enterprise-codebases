"""Script to generate themes and sectors market share trend chart excluding finance."""

import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_themes_sectors_datasets
from chart_styles import (
    get_themes_sectors_color_scheme, get_chart_config, style_axes
)


def create_themes_sectors_excl_finance_chart(datasets, output_path):
    """Create line chart showing themes and sectors market share trends excluding finance.
    
    Args:
        datasets: Dictionary of theme/sector names to (years, market_share) data
        output_path: Path to save the output PNG file
    """
    # Get configuration
    colors = get_themes_sectors_color_scheme()
    config = get_chart_config()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=config['figure_size'], dpi=config['dpi'])
    
    # Plot each theme/sector line, excluding Finance
    for name, (years, market_shares) in datasets.items():
        if name.lower() == 'finance':
            continue  # Skip finance
        color = colors.get(name, '#666666')
        ax.plot(
            years,
            market_shares,
            label=name,
            color=color,
            linewidth=config['line_width'],
            marker='o',
            markersize=config['marker_size'],
            markevery=10,  # Show markers every 10th point
            alpha=0.9
        )
    
    # Set labels and title
    ax.set_xlabel('Year', fontsize=config['label_size'], fontweight='bold')
    ax.set_ylabel('Market Share (%)', fontsize=config['label_size'], fontweight='bold')
    ax.set_title(
        'Themes & Sectors Market Share Trends (Excluding Finance) (2004-2025)',
        fontsize=config['title_size'],
        fontweight='bold',
        pad=20
    )
    
    # Apply styling
    style_axes(ax, config)
    
    # Set x-axis limits and ticks
    ax.set_xlim(2004, 2026)
    ax.set_xticks(range(2004, 2027, 2))
    
    # Set y-axis to start from 0
    ax.set_ylim(bottom=0)
    
    # Add legend
    legend = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        fontsize=config['legend_size'],
        frameon=False
    )
    
    # Style legend lines
    for line in legend.get_lines():
        line.set_linewidth(3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the chart
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"Chart saved to: {output_path}")


def main():
    """Main execution function."""
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / 'api' / 'data' / 'manual' / 'year_market-share'
    output_dir = base_dir / 'reports'
    output_path = output_dir / 'themes_sectors_excl_finance_trends.png'
    
    # Load data
    print("Loading themes and sectors CSV data...")
    datasets = load_themes_sectors_datasets(str(data_dir))
    
    if not datasets:
        print("Error: No themes/sectors data files found!")
        return
    
    # Count datasets excluding finance
    non_finance_count = sum(1 for name in datasets if name.lower() != 'finance')
    
    print(f"Loaded {len(datasets)} themes/sectors datasets ({non_finance_count} excluding finance):")
    for name in datasets:
        years, shares = datasets[name]
        status = " (excluded)" if name.lower() == 'finance' else ""
        print(f"  - {name}: {len(years)} data points{status}")
    
    # Generate chart
    print("\nGenerating themes & sectors chart (excluding finance)...")
    create_themes_sectors_excl_finance_chart(datasets, str(output_path))
    print("Done!")


if __name__ == "__main__":
    main()