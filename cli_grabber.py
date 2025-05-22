#!/usr/bin/env python3
"""
Command-line interface for HuggingFace Paper Grabber

Provides a flexible command-line interface to download and categorize papers.
"""

import argparse
import sys
from hf_paper_grabber import HFPaperGrabber
from categorized_grabber import CategorizedPaperGrabber


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download research papers from HuggingFace's papers page."
    )
    
    parser.add_argument(
        "-l", "--limit", 
        type=int, 
        default=10,
        help="Maximum number of papers to download (default: 10)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="downloaded_papers",
        help="Directory to save downloaded papers (default: downloaded_papers)"
    )
    
    parser.add_argument(
        "-c", "--categorize",
        action="store_true",
        help="Categorize papers based on content and save to subdirectories"
    )
    
    parser.add_argument(
        "-f", "--filter",
        nargs="+",
        help="Filter papers by keywords in title (space-separated list)"
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
    print("HuggingFace Paper Grabber")
    print("=" * 80)
    
    # Print configuration
    print(f"URL: {args.url}")
    print(f"Output directory: {args.output_dir}")
    print(f"Paper limit: {args.limit}")
    
    if args.filter:
        print(f"Filtering by keywords: {', '.join(args.filter)}")
    
    if args.categorize:
        print("Mode: Categorized (papers will be organized by topic)")
        grabber = CategorizedPaperGrabber(base_url=args.url, output_dir=args.output_dir)
    else:
        print("Mode: Standard (papers will be saved to a single directory)")
        grabber = HFPaperGrabber(base_url=args.url, output_dir=args.output_dir)
    
    print("=" * 80)
    print()
    
    try:
        # Process papers
        if args.categorize:
            papers = grabber.process_papers(limit=args.limit, filter_keywords=args.filter)
        else:
            papers = grabber.get_paper_links(limit=args.limit)
            
            # Apply filtering if requested
            if args.filter and not isinstance(grabber, CategorizedPaperGrabber):
                filtered_papers = []
                for paper in papers:
                    title = paper['title'].lower()
                    if any(keyword.lower() in title for keyword in args.filter):
                        filtered_papers.append(paper)
                papers = filtered_papers
            
            # Process each paper
            processed_papers = []
            for paper in papers:
                paper_with_details = grabber.get_paper_details(paper)
                downloaded_paper = grabber.download_paper(paper_with_details)
                processed_papers.append(downloaded_paper)
        
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