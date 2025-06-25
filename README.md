# HuggingFace Paper Grabber

A Python utility to download research papers from HuggingFace's papers page with intelligent filtering options.

## Features

- Scrapes papers from https://huggingface.co/papers
- Downloads PDFs and their abstracts
- Multiple filtering modes:
  - **Rule-based filtering**: Use built-in or custom Python functions
  - **LLM-based filtering**: Use Claude 3.7 via LiteLLM for intelligent evaluation
- Single unified command-line interface
- Configurable output directories and download limits

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

### Main Command

All functionality is accessed through a single entry point:

```bash
python main.py [options]
```

### Basic Usage Examples

**Default LLM-based filtering:**
```bash
python main.py
```

**Rule-based filtering:**
```bash
python main.py --mode rule-based
```

**Custom criteria file:**
```bash
python main.py --criteria-file my_criteria.txt
```

**Download more papers to custom directory:**
```bash
python main.py --max-downloads 20 --output-dir research_papers
```

**Use custom rule-based filter:**
```bash
python main.py --mode rule-based --filter-module sample_filters.py
```

### Command Options

**Core Options:**
- `--mode {rule-based,llm}`: Filtering mode (default: llm)
- `-n, --max-downloads N`: Maximum papers to download (default: 10)
- `-o, --output-dir DIR`: Save papers to DIR (default: papers)
- `-u, --url URL`: Source URL (default: https://huggingface.co/papers)

**Rule-based Mode Options:**
- `-f, --filter-module FILE`: Path to custom Python filter module

**LLM Mode Options:**
- `-c, --criteria-file FILE`: Path to criteria file (default: what_makes_a_good_paper.txt)
- `-m, --model MODEL`: LLM model to use (default: anthropic/claude-sonnet-4-20250514)
- `-s, --min-score N`: Minimum score threshold (1-10) to download

**Future Options:**
- `--upload-server URL`: Upload endpoint (not yet implemented)

## Filtering Modes

### Rule-Based Filtering

Uses Python functions to evaluate papers based on title and abstract content. 

**Built-in filters** (in `sample_filters.py`):
- `should_download`: Selects AI-related papers
- `ml_focus_filter`: Machine learning focused papers
- `nlp_only_filter`: Natural language processing papers only
- `vision_only_filter`: Computer vision papers only

**Custom filters**: Create a Python file with a `should_download(abstract, title)` function.

### LLM-Based Filtering

Uses Claude 3.7 to intelligently evaluate papers against custom criteria.

**How it works:**
1. Reads evaluation criteria from a text file
2. For each paper, sends title and abstract to Claude along with your criteria
3. Claude returns a boolean decision, relevance score (1-10), and reasoning
4. Papers meeting criteria are downloaded
5. Detailed evaluation summary is saved

**Criteria file format:**
```
Good papers should focus on machine learning applications in healthcare.
They should present novel approaches, be well-structured, and include
experimental results with real-world data.
```

**Example with monkey criteria:**
```bash
echo "Good papers involve monkeys." > monkey_criteria.txt
python main.py --criteria-file monkey_criteria.txt
```

## Output Structure

Downloaded papers are organized as:

```
papers/  (or your custom output directory)
├── abstracts/
│   ├── 01_paper_title.txt
│   ├── 02_paper_title.txt
│   └── ...
└── pdfs/
    ├── 01_paper_title.pdf
    ├── 02_paper_title.pdf
    └── ...
```

For LLM mode, an additional `evaluation_summary.txt` file contains detailed evaluation results.

## Future Development

- Server upload functionality for processed papers
- Additional paper repositories beyond HuggingFace
- Text analysis and citation extraction
- Impact and popularity metrics integration