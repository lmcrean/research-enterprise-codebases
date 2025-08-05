"""Chart styling configuration for market share visualization."""

from typing import Dict, Tuple


def get_color_scheme() -> Dict[str, str]:
    """Get distinct colors for each technology using CMYK + purple.
    
    Returns:
        Dictionary mapping technology names to hex colors
    """
    return {
        'Artificial Intelligence': '#00FFFF',  # Cyan
        'Devops': '#FF00FF',                  # Magenta  
        'Machine Learning': '#FFA500',         # Yellow
        'Software Engineering': '#000000',     # Black (Key)
        'Web Development': '#8B4789'           # Purple (distinct)
    }


def get_chart_config() -> Dict:
    """Get chart configuration settings.
    
    Returns:
        Dictionary with chart configuration parameters
    """
    return {
        'figure_size': (14, 8),
        'dpi': 100,
        'title_size': 16,
        'label_size': 12,
        'legend_size': 10,
        'line_width': 2.5,
        'grid_alpha': 0.3,
        'grid_style': '--',
        'marker_size': 4
    }


def style_axes(ax, config: Dict) -> None:
    """Apply styling to chart axes.
    
    Args:
        ax: Matplotlib axes object
        config: Chart configuration dictionary
    """
    # Grid styling
    ax.grid(True, alpha=config['grid_alpha'], linestyle=config['grid_style'])
    ax.set_axisbelow(True)
    
    # Spine styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=config['label_size'])
    ax.tick_params(axis='x', rotation=45)


def format_legend(ax, config: Dict) -> None:
    """Format and position the legend.
    
    Args:
        ax: Matplotlib axes object
        config: Chart configuration dictionary
    """
    legend = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=5,
        fontsize=config['legend_size'],
        frameon=False
    )
    
    # Style legend lines
    for line in legend.get_lines():
        line.set_linewidth(3)