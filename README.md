# HuggingFace Paper Grabber

A Python tool for automatically downloading and filtering research papers from HuggingFace's papers page using LLM-based evaluation, with automatic Google Drive upload capabilities.

## Features

- **Intelligent Filtering**: Uses Claude 3.7 or other LLMs to evaluate papers based on custom criteria
- **Google Drive Integration**: Automatically upload filtered papers to Google Drive
- **Configurable Downloads**: Set maximum number of papers to download
- **Smart Organization**: Automatically organizes papers into PDFs and abstracts
- **Evaluation Reports**: Generates detailed evaluation summaries
- **Multiple Filter Modes**: Rule-based or LLM-based filtering
- **Custom Criteria**: Define your own evaluation criteria
- **Environment Variables**: Centralized configuration via `.env` file

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd huggingface-paper-grabber
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

4. **Run with default settings**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM Configuration
LLM_MODEL=anthropic/claude-sonnet-4-20250514

# API Keys (use provider-specific names)
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-openai-key-here
# GOOGLE_API_KEY=your-google-api-key-here

# Google Drive Upload Configuration
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_FOLDER_NAME=HuggingFace Papers

# Service Account JSON (alternative to credentials file)
# GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}

# Paper Download Configuration
MAX_DOWNLOADS=10
OUTPUT_DIR=filtered_papers
CRITERIA_FILE=what_makes_a_good_paper.txt
MIN_SCORE=0

# HuggingFace Papers URL
HUGGINGFACE_URL=https://huggingface.co/papers

# Upload Configuration
UPLOAD_TO_DRIVE=true
```

### Google Drive Setup

**Option 1: Service Account (Recommended for automation)**
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create a service account
4. Download the service account JSON file
5. Set `GOOGLE_DRIVE_CREDENTIALS_PATH` to the file path, or
6. Set `GOOGLE_SERVICE_ACCOUNT_JSON` with the JSON content directly

**Option 2: OAuth (Interactive)**
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download the credentials JSON file
3. Set `GOOGLE_DRIVE_CREDENTIALS_PATH` to the file path

### Command Line Options

```bash
python main.py [options]

Options:
  -n, --max-downloads N           Maximum papers to download
  -c, --criteria-file FILE        Custom evaluation criteria file
  -m, --model MODEL               LLM model to use
  -o, --output-dir DIR            Output directory
  --mode MODE                     Filter mode: llm or rule-based
  --one-paper                     Download only one paper for testing
  --upload-to-drive               Upload papers to Google Drive
  --drive-credentials FILE        Google Drive credentials file
  --drive-folder NAME             Google Drive folder name
```

## Examples

### Basic Usage
```bash
# Download up to 10 papers using default criteria
python main.py

# Download 20 papers to a custom directory
python main.py -n 20 -o my_filtered_papers

# Test with one paper
python main.py --one-paper
```

### With Google Drive Upload
```bash
# Download and upload to Google Drive
python main.py --upload-to-drive

# With custom credentials file
python main.py --upload-to-drive --drive-credentials service-account.json

# To a specific Google Drive folder
python main.py --upload-to-drive --drive-folder "AI Research Papers"
```

### Custom Filtering
```bash
# Use custom evaluation criteria
python main.py -c my_criteria.txt

# Use different LLM model
python main.py -m openai/gpt-4o

# Rule-based filtering
python main.py --mode rule-based

# Set minimum score threshold
python main.py -s 7  # Only download papers scoring 7/10 or higher
```

## Evaluation Criteria

The tool uses a text file to define what makes a good paper. Edit `what_makes_a_good_paper.txt` to customize the evaluation criteria.

Example criteria:
```
Papers should focus on AI agents that perform tool use - systems where AI agents can select and use external tools, APIs, or instruments to accomplish tasks. This includes but is not limited to:

1. AI agents using APIs, databases, or external services
2. Tool-calling and function-calling language models
3. Robotic systems where AI controls tools or instruments
4. Multi-agent systems with tool coordination
5. Agent frameworks that enable tool use

Exclude papers that are only about:
- Pure language model training or inference
- Computer vision without tool use
- Basic machine learning algorithms
- Theoretical AI without implementation
```

## Output Structure

The tool only stores papers that **pass the filter criteria** - rejected papers are not saved to disk, keeping your storage clean and organized.

```
filtered_papers/              # Only papers that passed the filter
├── pdfs/                     # Downloaded PDF files
│   ├── 01_paper_title.pdf
│   ├── 02_paper_title.pdf
│   └── ...
├── abstracts/                # Paper abstracts as text files
│   ├── 01_paper_title.txt
│   ├── 02_paper_title.txt
│   └── ...
└── evaluation_summary.txt    # Detailed evaluation report (includes all papers evaluated)
```

**Key Design Decisions:**
- **Only filtered papers are stored**: Papers that don't meet your criteria are evaluated but not downloaded, saving disk space and keeping your collection focused
- **Complete evaluation log**: All papers (accepted and rejected) are documented in `evaluation_summary.txt` with scores and reasoning
- **Clear naming**: The `filtered_papers` directory name makes it obvious these are curated results, not raw downloads
- **Configurable location**: Change the output directory via `OUTPUT_DIR` in `.env` or `--output-dir` flag
- **Efficient workflow**: The LLM evaluates abstracts first, only downloading PDFs for papers that pass your criteria

## Supported LLM Models

Configure via `LLM_MODEL` environment variable:

- `anthropic/claude-sonnet-4-20250514` (recommended)
- `openai/gpt-4o`
- `google/gemini-1.5-pro`
- `meta-llama/llama-3.1-405b-instruct`

## Requirements

- Python 3.8+
- LiteLLM library for LLM integration
- BeautifulSoup for web scraping
- Requests for HTTP handling
- Google API Client for Drive integration
- python-dotenv for environment variables

## API Keys

For LLM-based filtering, set the appropriate environment variable:

- **Anthropic Claude**: `ANTHROPIC_API_KEY=sk-ant-...`
- **OpenAI GPT**: `OPENAI_API_KEY=sk-...`
- **Google Gemini**: `GOOGLE_API_KEY=AI...`

The tool automatically uses the correct API key based on the model specified in `LLM_MODEL`.

## Security Notes

- Never commit your `.env` file to version control
- Use service accounts for Google Drive in production environments
- Rotate API keys regularly
- Consider using environment variables or secret management in production

## License

MIT License - see LICENSE file for details.