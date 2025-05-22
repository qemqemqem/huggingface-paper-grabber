#!/usr/bin/env python3
"""
LLM-filtered HuggingFace Paper Grabber

Uses LiteLLM and Claude 3.7 to evaluate and filter papers based on custom criteria.
"""

import argparse
import sys
import os
from filtered_paper_grabber import FilteredPaperGrabber
import llm_filter


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download research papers from HuggingFace using LLM-based filtering."
    )
    
    parser.add_argument(
        "-n", "--max-downloads", 
        type=int, 
        default=5,
        help="Maximum number of papers to download after filtering (default: 5)"
    )
    
    parser.add_argument(
        "-c", "--criteria-file",
        type=str,
        default="what_makes_a_good_paper.txt",
        help="Path to the criteria prompt file (default: what_makes_a_good_paper.txt)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="llm_filtered_papers",
        help="Directory to save downloaded papers (default: llm_filtered_papers)"
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        default="https://huggingface.co/papers",
        help="URL to scrape papers from (default: https://huggingface.co/papers)"
    )
    
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="claude-3-7-sonnet",
        help="LLM model to use for evaluation (default: claude-3-7-sonnet)"
    )
    
    parser.add_argument(
        "-s", "--min-score",
        type=int,
        default=0,
        help="Minimum relevance score (1-10) required to download (default: 0, meaning use the boolean decision only)"
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
    
    def process_papers(self, max_downloads=5):
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
    
    # Check if criteria file exists
    if not os.path.exists(args.criteria_file):
        print(f"Error: Criteria file not found: {args.criteria_file}")
        sys.exit(1)
    
    # Print banner
    print("=" * 80)
    print("HuggingFace Paper Grabber (LLM-Filtered Version)")
    print("=" * 80)
    
    # Print configuration
    print(f"URL: {args.url}")
    print(f"Output directory: {args.output_dir}")
    print(f"Maximum downloads: {args.max_downloads}")
    print(f"Criteria file: {args.criteria_file}")
    print(f"LLM model: {args.model}")
    if args.min_score > 0:
        print(f"Minimum score threshold: {args.min_score}/10")
    
    print("=" * 80)
    print()
    
    try:
        # Initialize grabber and process papers
        grabber = LLMFilteredPaperGrabber(
            base_url=args.url, 
            output_dir=args.output_dir,
            criteria_file=args.criteria_file,
            model=args.model,
            min_score=args.min_score
        )
        processed_papers = grabber.process_papers(max_downloads=args.max_downloads)
        
        # Print completion message
        print("\nDownload complete!")
        print(f"Papers saved to: {args.output_dir}")
        print(f"Evaluation summary saved to: {args.output_dir}/evaluation_summary.txt")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()