"""Main script to generate market share trend chart."""

import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_all_datasets
from chart_styles import (
    get_color_scheme, get_chart_config, style_axes, format_legend
)


def create_market_share_chart(datasets, output_path):
    """Create line chart showing market share trends.
    
    Args:
        datasets: Dictionary of technology names to (years, market_share) data
        output_path: Path to save the output PNG file
    """
    # Get configuration
    colors = get_color_scheme()
    config = get_chart_config()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=config['figure_size'], dpi=config['dpi'])
    
    # Plot each technology line
    for tech_name, (years, market_shares) in datasets.items():
        color = colors.get(tech_name, '#666666')
        ax.plot(
            years,
            market_shares,
            label=tech_name,
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
        'Technology Market Share Trends (2004-2025)',
        fontsize=config['title_size'],
        fontweight='bold',
        pad=20
    )
    
    # Apply styling
    style_axes(ax, config)
    
    # Set x-axis limits and ticks
    ax.set_xlim(2004, 2025)
    ax.set_xticks(range(2004, 2026, 2))
    
    # Set y-axis to start from 0
    ax.set_ylim(bottom=0)
    
    # Add legend
    format_legend(ax, config)
    
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
    data_dir = base_dir / 'data' / 'manual' / 'year_market-share'
    output_dir = base_dir / 'docs' / 'market-report'
    output_path = output_dir / 'technology_market_trends.png'
    
    # Load data
    print("Loading CSV data...")
    datasets = load_all_datasets(str(data_dir))
    
    if not datasets:
        print("Error: No data files found!")
        return
    
    print(f"Loaded {len(datasets)} datasets:")
    for tech_name in datasets:
        years, shares = datasets[tech_name]
        print(f"  - {tech_name}: {len(years)} data points")
    
    # Generate chart
    print("\nGenerating chart...")
    create_market_share_chart(datasets, str(output_path))
    print("Done!")


if __name__ == "__main__":
    main()