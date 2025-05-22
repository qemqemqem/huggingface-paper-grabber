# HuggingFace Paper Grabber

A Python utility to download research papers from HuggingFace's papers page based on content filtering.

## Features

- Scrapes papers from https://huggingface.co/papers
- Downloads PDFs and their abstracts
- Multiple filtering options:
  - Simple keyword-based filtering
  - Rule-based filtering with custom functions
  - LLM-based filtering using Claude 3.7 via LiteLLM
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

3. For LLM-based filtering, set up API access:
   ```bash
   # For Anthropic API (Claude)
   export ANTHROPIC_API_KEY=your_api_key_here
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

### Using LLM-Based Filtering

For more sophisticated filtering using an LLM:

```bash
python llm_filtered_cli.py [options]
```

Options:
- `-n, --max-downloads N`: Download up to N papers (default: 5)
- `-c, --criteria-file FILE`: Path to criteria prompt file (default: what_makes_a_good_paper.txt)
- `-o, --output-dir DIR`: Save papers to DIR (default: llm_filtered_papers)
- `-m, --model MODEL`: LLM model to use (default: claude-3-7-sonnet)
- `-s, --min-score N`: Minimum score threshold (1-10) required to download
- `-u, --url URL`: Use a different URL (default: https://huggingface.co/papers)

Examples:

```bash
# Basic usage with default criteria
python llm_filtered_cli.py

# Use custom criteria file with minimum score threshold
python llm_filtered_cli.py --criteria-file my_criteria.txt --min-score 7

# Download more papers
python llm_filtered_cli.py --max-downloads 10 --output-dir more_papers
```

### Using Custom Rule-Based Filtering

For rule-based filtering:

```bash
python filtered_cli.py [options]
```

Options:
- `-n, --max-downloads N`: Download up to N papers (default: 10)
- `-o, --output-dir DIR`: Save papers to DIR (default: filtered_papers)
- `-f, --filter-module PATH`: Use a custom filter module
- `-u, --url URL`: Use a different URL (default: https://huggingface.co/papers)

## LLM-Based Filtering

### How It Works

The LLM-based filter:
1. Reads your criteria from a prompt file
2. For each paper, sends the abstract and title to Claude 3.7 along with your criteria
3. The LLM evaluates the paper and returns:
   - A boolean decision (should download or not)
   - A relevance score (1-10)
   - Reasoning for the evaluation
4. Papers that meet the criteria are downloaded
5. A summary of all evaluations is saved

### Criteria File Format

The criteria file should contain the standards by which papers should be evaluated. For example:

```
Good papers should focus on machine learning applications in healthcare.
They should present novel approaches, be well-structured, and include
experimental results with real-world data.
```

### Evaluation Summary

After running, an `evaluation_summary.txt` file is created in the output directory with detailed information about each paper evaluation, including scores and reasoning.

## Custom Rule-Based Filtering

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