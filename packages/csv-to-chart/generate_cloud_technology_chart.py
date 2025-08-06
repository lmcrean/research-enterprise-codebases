"""Script to generate cloud and technology infrastructure trend chart."""

import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_cloud_technology_datasets
from chart_styles import (
    get_cloud_technology_color_scheme, get_chart_config, style_axes
)


def create_cloud_technology_chart(datasets, output_path):
    """Create line chart showing cloud and technology market share trends.
    
    Args:
        datasets: Dictionary of cloud/tech names to (years, market_share) data
        output_path: Path to save the output PNG file
    """
    # Get configuration
    colors = get_cloud_technology_color_scheme()
    config = get_chart_config()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=config['figure_size'], dpi=config['dpi'])
    
    # Plot each cloud/technology line
    for tech_name, (years, market_shares) in datasets.items():
        color = colors.get(tech_name, '#666666')
        ax.plot(
            years,
            market_shares,
            label=tech_name.upper() if tech_name in ['Aws', 'Gcp'] else tech_name,
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
        'Cloud & Technology Infrastructure Market Share Trends (2004-2025)',
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
        ncol=3,
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
    output_path = output_dir / 'cloud_technology_trends.png'
    
    # Load data
    print("Loading cloud and technology CSV data...")
    datasets = load_cloud_technology_datasets(str(data_dir))
    
    if not datasets:
        print("Error: No cloud/technology data files found!")
        return
    
    print(f"Loaded {len(datasets)} cloud/technology datasets:")
    for tech_name in datasets:
        years, shares = datasets[tech_name]
        print(f"  - {tech_name}: {len(years)} data points")
    
    # Generate chart
    print("\nGenerating cloud & technology chart...")
    create_cloud_technology_chart(datasets, str(output_path))
    print("Done!")


if __name__ == "__main__":
    main()