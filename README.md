# Research Enterprise Codebases 📊

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub API](https://img.shields.io/badge/GitHub-API%20v3-black.svg)](https://docs.github.com/en/rest)

A comprehensive analysis tool for examining GitHub repository statistics across different technology categories including AI/ML, TypeScript, and C# ASP.NET projects.

## 🎯 Overview

This project collects and analyzes repository statistics from 55+ popular open-source enterprise codebases, providing insights into:
- Star counts and popularity trends
- Fork and contributor statistics
- Pull request activity
- Technology stack distributions
- Repository health metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- GitHub personal access token (for API access)
- Jupyter Notebook

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/research-enterprise-codebases.git
cd research-enterprise-codebases
```

2. Install dependencies:
```bash
pip install requests pandas jupyter python-dotenv
```

3. Create a `.env` file with your GitHub token:
```bash
echo "GITHUB_TOKEN=your_github_token_here" > .env
```

### Usage

#### 1. Verify Setup
Test your configuration:
```bash
python quick_test.py
```

#### 2. Collect Data
Run the data collection notebook to fetch fresh statistics:
```bash
jupyter notebook github_data_collector.ipynb
```

This will:
- Fetch repository data from GitHub API
- Handle rate limiting automatically
- Save results to `github_repository_stats.csv`
- Create metadata file with collection timestamp

#### 3. View Results
Open the viewer notebook to see formatted statistics:
```bash
jupyter notebook github_stats_viewer.ipynb
```

Features:
- Summary statistics cards
- Technology-grouped repository tables
- Top 10 most starred repositories
- Visual progress bars for metrics

## 📁 Project Structure

```
research-enterprise-codebases/
├── quick_test.py                    # API connection verification
├── github_data_collector.ipynb      # Data collection notebook
├── github_stats_viewer.ipynb        # Results visualization
├── github_repository_stats.csv      # Collected statistics (generated)
├── github_stats_metadata.json       # Collection metadata (generated)
├── CLAUDE.md                        # AI assistant instructions
├── .env                             # GitHub token (create this)
└── README.md                        # This file
```

## 📊 Repository Categories

The analysis covers three main technology categories:

### AI/ML Repositories
- TensorFlow, PyTorch, scikit-learn
- Hugging Face Transformers
- FastAPI, Streamlit
- And more...

### TypeScript Projects
- Angular, Vue.js, Next.js
- NestJS, TypeORM
- Storybook, Playwright
- And more...

### C# ASP.NET Projects
- ASP.NET Core, Entity Framework
- Orleans, MassTransit
- Ocelot, IdentityServer4
- And more...

## 🔧 Configuration

### GitHub Token
The project requires a GitHub personal access token for API access:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `public_repo` scope
3. Add to `.env` file as `GITHUB_TOKEN=your_token_here`

### API Rate Limits
- With token: 5,000 requests/hour
- Without token: 60 requests/hour
- The collector implements automatic rate limit handling

## 📈 Output Examples

The viewer notebook displays:

### Summary Cards
```
Total Repositories: 55
Total Stars: 1,234,567
Total Forks: 345,678
Average Stars: 22,446
```

### Repository Tables
Styled tables showing:
- Repository name and owner
- Star count with visual bars
- Fork count
- Open issues
- Contributor count
- Last update date

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GitHub API for providing comprehensive repository data
- All the amazing open-source projects analyzed in this study
