# HuggingFace Paper Grabber

A Python utility to download research papers from HuggingFace's papers page.

## Features

- Scrapes the top papers from https://huggingface.co/papers
- Downloads paper PDFs and their abstracts
- Organizes downloads in structured folders
- Filters papers based on keywords
- Categorizes papers by content type (NLP, Computer Vision, etc.)
- Command-line interface for flexible usage

## Requirements

- Python 3.6+
- Dependencies: see requirements.txt

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/huggingface-paper-grabber.git
   cd huggingface-paper-grabber
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the script directly:

```bash
# Activate the virtual environment if not already activated
source venv/bin/activate

# Run the paper grabber (2024 version)
python hf_paper_grabber_updated.py
```

By default, it will:
- Download the top 10 papers from HuggingFace
- Save PDFs to `downloaded_papers/pdfs/`
- Save abstracts to `downloaded_papers/abstracts/`

### Using the Command-Line Interface

For more flexibility, use the CLI tool:

```bash
python cli_grabber_updated.py [options]
```

Options:
- `-l, --limit N`: Download up to N papers (default: 10)
- `-o, --output-dir DIR`: Save papers to DIR (default: downloaded_papers)
- `-c, --categorize`: Organize papers by topic (NLP, vision, etc.)
- `-f, --filter KEYWORDS`: Only download papers with these keywords in the title
- `-u, --url URL`: Use a different URL (default: https://huggingface.co/papers)

Examples:

```bash
# Download top 20 papers
python cli_grabber_updated.py --limit 20

# Download and categorize papers
python cli_grabber_updated.py --categorize

# Download only papers about transformers or diffusion
python cli_grabber_updated.py --filter transformer diffusion

# Combine options
python cli_grabber_updated.py --limit 30 --categorize --filter llm vision --output-dir ai_papers
```

### Using the Categorized Grabber

For automatic categorization:

```bash
python categorized_grabber_updated.py
```

This will:
- Download papers from HuggingFace
- Categorize them based on content
- Save them to category-specific directories

## Customization

The script is designed to be extended with custom filtering and categorization:

```python
from hf_paper_grabber_updated import HFPaperGrabber

class CustomGrabber(HFPaperGrabber):
    def filter_papers(self, papers):
        """Filter papers based on custom criteria"""
        filtered = []
        for paper in papers:
            # Example: Only keep papers with "transformer" in the title
            if "transformer" in paper['title'].lower():
                filtered.append(paper)
        return filtered
    
    def categorize_paper(self, paper):
        """Categorize papers based on their content"""
        # Example: Check abstract for keywords
        abstract = paper['abstract'].lower()
        if "nlp" in abstract or "language" in abstract:
            return "nlp"
        elif "vision" in abstract or "image" in abstract:
            return "vision"
        else:
            return "general"

# Usage
grabber = CustomGrabber()
papers = grabber.get_paper_links(limit=20)
papers = grabber.filter_papers(papers)

for paper in papers:
    paper = grabber.get_paper_details(paper)
    category = grabber.categorize_paper(paper)
    # Save to category-specific directory
    # ...
```

## Directory Structure

When using categorization, papers will be organized as follows:

```
categorized_papers/
├── abstracts/
│   ├── nlp/
│   │   ├── 01_paper_title.txt
│   │   └── ...
│   ├── vision/
│   │   ├── 02_paper_title.txt
│   │   └── ...
│   └── ...
└── pdfs/
    ├── nlp/
    │   ├── 01_paper_title.pdf
    │   └── ...
    ├── vision/
    │   ├── 02_paper_title.pdf
    │   └── ...
    └── ...
```

## Future Development

- Add content-based filtering using NLP techniques
- Implement citation extraction
- Add support for other paper repositories
- Create a web interface

## Version History

- v1.0.0 - Initial release
- v1.1.0 - Updated for 2024 HuggingFace website structure