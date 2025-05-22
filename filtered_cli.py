#!/usr/bin/env python3
"""
Command-line interface for Filtered HuggingFace Paper Grabber

Provides a CLI for downloading papers based on abstract content filtering.
"""

import argparse
import sys
import importlib.util
import os
from filtered_paper_grabber import FilteredPaperGrabber


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
        description="Download research papers from HuggingFace's papers page with content filtering."
    )
    
    parser.add_argument(
        "-n", "--max-downloads", 
        type=int, 
        default=10,
        help="Maximum number of papers to download after filtering (default: 10)"
    )
    
    parser.add_argument(
        "-f", "--filter-module",
        type=str,
        help="Path to a Python file with a custom should_download function"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="filtered_papers",
        help="Directory to save downloaded papers (default: filtered_papers)"
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        default="https://huggingface.co/papers",
        help="URL to scrape papers from (default: https://huggingface.co/papers)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Print banner
    print("=" * 80)
    print("HuggingFace Paper Grabber (Filtered Version)")
    print("=" * 80)
    
    # Print configuration
    print(f"URL: {args.url}")
    print(f"Output directory: {args.output_dir}")
    print(f"Maximum downloads: {args.max_downloads}")
    
    # Load custom filter if provided
    if args.filter_module:
        print(f"Using custom filter module: {args.filter_module}")
        filter_module = load_filter_module(args.filter_module)
        
        # Replace the should_download function in paper_filter with the custom one
        import paper_filter
        paper_filter.should_download = filter_module.should_download
    
    print("=" * 80)
    print()
    
    try:
        # Initialize grabber and process papers
        grabber = FilteredPaperGrabber(base_url=args.url, output_dir=args.output_dir)
        processed_papers = grabber.process_papers(max_downloads=args.max_downloads)
        
        # Print completion message
        print("\nDownload complete!")
        print(f"Papers saved to: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()