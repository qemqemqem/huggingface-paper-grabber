# HuggingFace Paper Grabber

A Python utility to download research papers from HuggingFace's papers page based on content filtering.

## Features

- Scrapes papers from https://huggingface.co/papers
- Downloads PDFs and their abstracts
- Filters papers based on abstract content
- Supports custom filter functions
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

Run the filtered paper grabber:

```bash
source venv/bin/activate
python filtered_paper_grabber.py
```

By default, it will:
- Analyze papers from HuggingFace's papers page
- Download up to 10 papers that pass the filter
- Save PDFs to `filtered_papers/pdfs/`
- Save abstracts to `filtered_papers/abstracts/`

### Using the Command-Line Interface

For more flexibility, use the CLI tool:

```bash
python filtered_cli.py [options]
```

Options:
- `-n, --max-downloads N`: Download up to N papers (default: 10)
- `-o, --output-dir DIR`: Save papers to DIR (default: filtered_papers)
- `-f, --filter-module PATH`: Use a custom filter module
- `-u, --url URL`: Use a different URL (default: https://huggingface.co/papers)

Examples:

```bash
# Download up to 20 papers
python filtered_cli.py --max-downloads 20

# Use a custom filter module
python filtered_cli.py --filter-module sample_filters.py

# Combine options
python filtered_cli.py --max-downloads 15 --filter-module my_filter.py --output-dir ai_papers
```

## Custom Filtering

The key to this tool is the ability to create custom filters. A filter is a function that analyzes a paper's abstract and decides whether to download it.

### How Filtering Works

1. Create a Python module with a `should_download` function
2. The function should accept an abstract (and optionally a title)
3. Return `True` to download the paper, or `False` to skip it

### Example Filter Module

Here's a simple filter module:

```python
def should_download(abstract, title=""):
    """
    Determine if a paper should be downloaded.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str, optional): The title of the paper
        
    Returns:
        bool: True if the paper should be downloaded
    """
    # Convert to lowercase for case-insensitive matching
    text = (abstract + " " + title).lower()
    
    # Only download papers about transformers or LLMs
    target_topics = ["transformer", "llm", "large language model"]
    
    # Return True if any topic is found
    return any(topic in text for topic in target_topics)
```

### Sample Filters

The repository includes `sample_filters.py` with several example filters:

- `should_download`: Selects papers about AI topics
- `ml_focus_filter`: Selects machine learning focused papers
- `nlp_only_filter`: Selects only NLP papers
- `vision_only_filter`: Selects only computer vision papers

To use any of these filters, edit `paper_filter.py` to import and use the desired function, or use the CLI with the `--filter-module` option.

## Directory Structure

After running the tool, you'll have a structure like:

```
filtered_papers/
├── abstracts/
│   ├── 01_paper_title.txt
│   ├── 02_paper_title.txt
│   └── ...
└── pdfs/
    ├── 01_paper_title.pdf
    ├── 02_paper_title.pdf
    └── ...
```

## Future Development

- Add text analysis for more sophisticated filtering
- Implement citation extraction
- Add support for other paper repositories
- Create filtering based on paper impact or popularity metrics