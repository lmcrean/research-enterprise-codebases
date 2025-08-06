"""Chart styling configuration for market share visualization."""

from typing import Dict, Tuple


def get_color_scheme() -> Dict[str, str]:
    """Get distinct colors for each technology using CMYK + purple.
    
    Returns:
        Dictionary mapping technology names to hex colors
    """
    return {
        'Artificial Intelligence': '#00FFFF',  # Cyan
        'Data Analytics': '#FF0000',           # Red
        'Data Science': '#00FF00',             # Green
        'Devops': '#FF00FF',                  # Magenta  
        'Machine Learning': '#FFA500',         # Orange
        'Software Engineering': '#000000',     # Black (Key)
        'Web Development': '#8B4789'           # Purple (distinct)
    }


def get_language_color_scheme() -> Dict[str, str]:
    """Get distinct colors for programming languages.
    
    Returns:
        Dictionary mapping language names to hex colors
    """
    return {
        'C#': '#0000FF',           # Blue
        'Java': '#FF0000',         # Red
        'Javascript': '#F7DF1E',   # JavaScript Yellow
        'Python': '#00FF00',       # Bright Green
        'TypeScript': '#3178C6'    # TypeScript Blue
    }


def get_chart_config() -> Dict:
    """Get chart configuration settings.
    
    Returns:
        Dictionary with chart configuration parameters
    """
    return {
        'figure_size': (14, 16),
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


def get_job_titles_color_scheme() -> Dict[str, str]:
    """Get very distinct colors for job titles to avoid confusion.
    
    Returns:
        Dictionary mapping job title names to hex colors
    """
    return {
        'Analyst': '#FF1493',           # Deep Pink
        'Cyber Security': '#00CED1',    # Dark Turquoise
        'Data Analytics': '#FF4500',    # Orange Red
        'Data Science': '#000000',      # Black
        'Devops': '#9370DB',           # Medium Purple
        'Software Engineering': '#1E90FF',  # Dodger Blue
        'Web Development': '#FFD700'    # Gold
    }


def get_cloud_technology_color_scheme() -> Dict[str, str]:
    """Get cloud-inspired colors for cloud providers and technologies.
    
    Returns:
        Dictionary mapping cloud/tech names to hex colors
    """
    return {
        # Cloud providers
        'Aws': '#FF9900',              # AWS Orange
        'Azure': '#0078D4',            # Azure Blue
        'Gcp': '#00FF00',              # Bright Green
        # Technologies
        'Docker': '#FF0000',           # Bright Red
        'Kubernetes': '#000000',       # Black
        'Terraform': '#7B42BC'         # Terraform Purple
    }


def get_themes_sectors_color_scheme() -> Dict[str, str]:
    """Get CMYK + distinctive colors for themes and sectors.
    
    Returns:
        Dictionary mapping theme/sector names to hex colors
    """
    return {
        # Themes - CMYK base colors
        'Artificial Intelligence': '#00FFFF',   # Cyan
        'Business Intelligence': '#FF00FF',     # Magenta
        'Machine Learning': '#FFFF00',          # Yellow
        'Risk Management': '#000000',           # Black (K)
        # Sectors - Distinctive colors
        'Customer Service': '#FF1493',          # Deep Pink
        'Finance': '#FF8C00',                   # Dark Orange
        'Law': '#808080',                       # Grey
        'Marketing': '#00FF00'                  # Bright Green
    }


def format_legend(ax, config: Dict) -> None:
    """Format and position the legend.
    
    Args:
        ax: Matplotlib axes object
        config: Chart configuration dictionary
    """
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