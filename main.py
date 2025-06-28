#!/usr/bin/env python3
"""
HuggingFace Paper Grabber - Main Entry Point

Downloads research papers from HuggingFace's papers page with configurable filtering.
Supports rule-based and LLM-based filtering modes.
"""

import argparse
import sys
import os
import importlib.util
from dotenv import load_dotenv
from filtered_paper_grabber import FilteredPaperGrabber
import llm_filter
import paper_filter
import google_drive_uploader

# Load environment variables from .env file
load_dotenv()


def load_filter_module(filter_module_path):
    """
    Dynamically load a custom filter module.
    
    Args:
        filter_module_path: Path to the Python file containing filter function
        
    Returns:
        Module object with the filter function
    """
    if not os.path.exists(filter_module_path):
        print(f"Error: Filter module file '{filter_module_path}' not found.")
        sys.exit(1)
        
    try:
        spec = importlib.util.spec_from_file_location("custom_filter", filter_module_path)
        custom_filter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_filter)
        
        # Validate that the module has a should_download function
        if not hasattr(custom_filter, 'should_download'):
            print(f"Error: Filter module must contain a 'should_download' function.")
            sys.exit(1)
            
        return custom_filter
    except Exception as e:
        print(f"Error loading filter module: {e}")
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download research papers from HuggingFace with intelligent filtering.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Filter Modes:
  rule-based    Use built-in or custom Python filtering functions
  llm           Use LLM (Claude) for intelligent paper evaluation

Examples:
  python main.py                                    # LLM filtering with default criteria
  python main.py --criteria custom.txt             # LLM with custom criteria  
  python main.py --mode rule-based                 # Basic rule-based filtering
  python main.py --mode rule-based --filter sample_filters.py  # Custom rule-based filter
  python main.py --max-downloads 20 --output research_papers
  python main.py --upload-to-drive --drive-credentials creds.json  # Upload to Google Drive
        """
    )
    
    # Core options
    parser.add_argument(
        "--mode", 
        choices=["rule-based", "llm"], 
        default="llm",
        help="Filtering mode to use (default: llm)"
    )
    
    parser.add_argument(
        "-n", "--max-downloads", 
        type=int, 
        default=int(os.getenv('MAX_DOWNLOADS', '50')),  # Download more papers by default
        help=f"Maximum number of papers to download (default: {os.getenv('MAX_DOWNLOADS', '50')})"
    )
    
    parser.add_argument(
        "--one-paper",
        action="store_true",
        help="Only process one paper for testing"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=os.getenv('OUTPUT_DIR', 'filtered_papers'),
        help=f"Directory to save filtered papers (default: {os.getenv('OUTPUT_DIR', 'filtered_papers')})"
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        default=os.getenv('HUGGINGFACE_URL', 'https://huggingface.co/papers'),
        help=f"URL to scrape papers from (default: {os.getenv('HUGGINGFACE_URL', 'https://huggingface.co/papers')})"
    )
    
    # Rule-based filtering options
    parser.add_argument(
        "-f", "--filter-module",
        type=str,
        help="Path to custom Python filter module (rule-based mode only)"
    )
    
    # LLM filtering options
    parser.add_argument(
        "-c", "--criteria-file",
        type=str,
        default=os.getenv('CRITERIA_FILE', 'what_makes_a_good_paper.txt'),
        help=f"Path to criteria file for LLM evaluation (default: {os.getenv('CRITERIA_FILE', 'what_makes_a_good_paper.txt')})"
    )
    
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=os.getenv('LLM_MODEL', 'anthropic/claude-sonnet-4-20250514'),
        help=f"LLM model for evaluation (default: {os.getenv('LLM_MODEL', 'anthropic/claude-sonnet-4-20250514')})"
    )
    
    parser.add_argument(
        "-s", "--min-score",
        type=int,
        default=int(os.getenv('MIN_SCORE', '0')),
        help=f"Minimum LLM score (1-10) required to download (default: {os.getenv('MIN_SCORE', '0')})"
    )
    
    # Google Drive upload options
    parser.add_argument(
        "--upload-to-drive", 
        action="store_true",
        default=True,  # Enable Google Drive upload by default
        help="Upload filtered papers to Google Drive after downloading (default: enabled)"
    )
    
    parser.add_argument(
        "--drive-credentials",
        type=str,
        default=os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
        help=f"Path to Google Drive credentials file (default: {os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'None')})"
    )
    
    parser.add_argument(
        "--drive-folder",
        type=str,
        default=os.getenv('GOOGLE_DRIVE_FOLDER_NAME', 'HuggingFace Papers'),
        help=f"Name of the Google Drive folder to upload to (default: {os.getenv('GOOGLE_DRIVE_FOLDER_NAME', 'HuggingFace Papers')})"
    )
    
    parser.add_argument(
        "--drive-folder-id",
        type=str,
        default=os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
        help=f"Google Drive folder ID to upload to (overrides --drive-folder)"
    )
    
    parser.add_argument(
        "--drive-max-uploads",
        type=int,
        default=int(os.getenv('DRIVE_MAX_UPLOADS', '3')),
        help=f"Maximum number of top-scored papers to upload to Google Drive (default: {os.getenv('DRIVE_MAX_UPLOADS', '3')})"
    )
    
    # Future: Upload options (placeholder)
    parser.add_argument(
        "--upload-server",
        type=str,
        help="Server endpoint to upload papers to (not yet implemented)"
    )
    
    return parser.parse_args()


class LLMFilteredPaperGrabber(FilteredPaperGrabber):
    """Paper grabber that uses LLM-based filtering."""
    
    def __init__(self, base_url, output_dir, criteria_file, model, min_score):
        """Initialize with LLM-specific parameters."""
        super().__init__(base_url, output_dir)
        self.criteria_file = criteria_file
        self.model = model
        self.min_score = min_score
        
        # Store evaluation results for reporting
        self.evaluations = []
    
    def process_papers(self, max_downloads=10):
        """
        Process papers with LLM evaluation.
        
        Args:
            max_downloads: Maximum number of papers to download after filtering
            
        Returns:
            List of processed paper information
        """
        # Configure the LLM filter with our criteria file and model
        llm_filter.CRITERIA_FILE = self.criteria_file
        llm_filter.MODEL = self.model
        
        # Get paper links (with a higher initial limit to allow for filtering)
        initial_limit = max(50, max_downloads * 3)  # Get plenty of candidates
        papers = self.get_paper_links(limit=initial_limit)
        
        # Get details and apply filtering
        filtered_papers = []
        downloaded_count = 0
        
        print(f"\nAnalyzing abstracts with LLM filter...")
        print(f"Using criteria from: {self.criteria_file}")
        print(f"Using model: {self.model}")
        if self.min_score > 0:
            print(f"Minimum required score: {self.min_score}/10")
        print()
        
        for paper in papers:
            # Stop if we've reached the max downloads
            if downloaded_count >= max_downloads:
                break
                
            # Get paper details including abstract
            paper_with_details = self.get_paper_details(paper)
            
            # Get the full evaluation
            evaluation = llm_filter.evaluate_paper_with_llm(
                paper_with_details['abstract'], 
                paper_with_details['title'],
                self.model,
                self.criteria_file
            )
            
            # Store the evaluation
            paper_with_details['evaluation'] = evaluation
            self.evaluations.append({
                'title': paper_with_details['title'],
                'evaluation': evaluation
            })
            
            # Apply both the boolean decision and minimum score threshold
            should_download = evaluation['should_download']
            if self.min_score > 0:
                should_download = should_download and evaluation['relevance_score'] >= self.min_score
            
            if should_download:
                print(f"✓ Paper accepted: {paper['title']}")
                print(f"  Score: {evaluation['relevance_score']}/10")
                print(f"  Reasoning: {evaluation['reasoning']}")
                
                # Download the paper
                downloaded_paper = self.download_paper(paper_with_details)
                filtered_papers.append(downloaded_paper)
                downloaded_count += 1
            else:
                print(f"✗ Paper rejected: {paper['title']}")
                print(f"  Score: {evaluation['relevance_score']}/10")
                print(f"  Reasoning: {evaluation['reasoning']}")
            
            print()
            
        # Generate a summary of evaluations
        self._save_evaluation_summary()
        
        print(f"\nDownloaded {downloaded_count} papers after LLM filtering")
        return filtered_papers
    
    def _save_evaluation_summary(self):
        """Save a summary of all paper evaluations."""
        summary_path = os.path.join(self.output_dir, "evaluation_summary.txt")
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("# Paper Evaluation Summary\n\n")
                f.write(f"Criteria file: {self.criteria_file}\n")
                f.write(f"Model: {self.model}\n")
                f.write(f"Minimum score threshold: {self.min_score}/10\n\n")
                
                f.write("## Evaluations\n\n")
                
                # Sort by score (descending)
                sorted_evals = sorted(
                    self.evaluations, 
                    key=lambda x: x['evaluation']['relevance_score'], 
                    reverse=True
                )
                
                for item in sorted_evals:
                    eval_data = item['evaluation']
                    f.write(f"### {item['title']}\n")
                    f.write(f"* Decision: {'Download' if eval_data['should_download'] else 'Reject'}\n")
                    f.write(f"* Score: {eval_data['relevance_score']}/10\n")
                    f.write(f"* Reasoning: {eval_data['reasoning']}\n\n")
                
            print(f"Evaluation summary saved to: {summary_path}")
            
        except Exception as e:
            print(f"Error saving evaluation summary: {e}")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Print banner
    print("=" * 80)
    print("HuggingFace Paper Grabber")
    print("=" * 80)
    
    # Print configuration
    print(f"Mode: {args.mode}")
    print(f"URL: {args.url}")
    print(f"Output directory: {args.output_dir}")
    print(f"Maximum downloads: {args.max_downloads}")
    
    if args.mode == "llm":
        # LLM mode validation
        if not os.path.exists(args.criteria_file):
            print(f"Error: Criteria file not found: {args.criteria_file}")
            sys.exit(1)
            
        print(f"Criteria file: {args.criteria_file}")
        print(f"LLM model: {args.model}")
        if args.min_score > 0:
            print(f"Minimum score threshold: {args.min_score}/10")
    else:
        # Rule-based mode
        if args.filter_module:
            print(f"Using custom filter module: {args.filter_module}")
            filter_module = load_filter_module(args.filter_module)
            # Replace the should_download function in paper_filter with the custom one
            paper_filter.should_download = filter_module.should_download
        else:
            print("Using default rule-based filter")
    
    # Google Drive upload configuration
    if args.upload_to_drive:
        print(f"Google Drive upload: Enabled")
        print(f"Drive folder: {args.drive_folder}")
        print(f"Max uploads: {args.drive_max_uploads} top-scored papers")
        if args.drive_credentials:
            print(f"Credentials file: {args.drive_credentials}")
    
    print("=" * 80)
    print()
    
    try:
        # Initialize the appropriate grabber based on mode
        if args.mode == "llm":
            grabber = LLMFilteredPaperGrabber(
                base_url=args.url, 
                output_dir=args.output_dir,
                criteria_file=args.criteria_file,
                model=args.model,
                min_score=args.min_score
            )
        else:
            grabber = FilteredPaperGrabber(
                base_url=args.url, 
                output_dir=args.output_dir
            )
        
        # Process papers
        max_downloads = 1 if args.one_paper else args.max_downloads
        processed_papers = grabber.process_papers(max_downloads=max_downloads)
        
        # Upload to Google Drive if requested
        if args.upload_to_drive and processed_papers:
            print(f"\n{'='*80}")
            print("UPLOADING TO GOOGLE DRIVE")
            print(f"{'='*80}")
            
            # Upload only the top-scored papers to Google Drive (separate from download limit)
            success, upload_results = google_drive_uploader.upload_papers_to_drive(
                papers_dir=args.output_dir,
                credentials_path=args.drive_credentials,
                folder_name=args.drive_folder,
                folder_id=args.drive_folder_id,
                max_uploads=args.drive_max_uploads  # Upload limit (default: 3) separate from download limit
            )
            
            if not success:
                print("Warning: Some files failed to upload to Google Drive")
            else:
                print("✓ All files successfully uploaded to Google Drive!")
        elif args.upload_to_drive and not processed_papers:
            print("\nNo papers were downloaded, skipping Google Drive upload")
        
        # Future: Upload to server if specified
        if args.upload_server:
            print(f"\nUpload to server feature not yet implemented")
            print(f"Planned upload endpoint: {args.upload_server}")
        
        # Print completion message
        print("\nDownload complete!")
        print(f"Papers saved to: {args.output_dir}")
        if args.mode == "llm":
            print(f"Evaluation summary saved to: {args.output_dir}/evaluation_summary.txt")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()