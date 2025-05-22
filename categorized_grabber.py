#!/usr/bin/env python3
"""
Categorized HuggingFace Paper Grabber

An extension of the base paper grabber that categorizes papers 
and saves them to different directories based on content.
"""

import os
import re
from hf_paper_grabber import HFPaperGrabber


class CategorizedPaperGrabber(HFPaperGrabber):
    """
    Enhanced version of HFPaperGrabber that adds filtering and categorization.
    
    Extends the base grabber to:
    1. Filter papers based on custom criteria
    2. Categorize papers based on their content
    3. Save papers to category-specific directories
    """
    
    def __init__(self, base_url="https://huggingface.co/papers", 
                 output_dir="categorized_papers"):
        """Initialize with category-specific directories."""
        super().__init__(base_url, output_dir)
        
        # Define categories
        self.categories = ["nlp", "vision", "audio", "reinforcement_learning", "other"]
        
        # Create category directories
        for category in self.categories:
            category_pdf_dir = os.path.join(self.papers_dir, category)
            category_abstract_dir = os.path.join(self.abstracts_dir, category)
            
            for directory in [category_pdf_dir, category_abstract_dir]:
                if not os.path.exists(directory):
                    os.makedirs(directory)
    
    def filter_papers(self, papers, keywords=None):
        """
        Filter papers based on title keywords.
        
        Args:
            papers: List of paper info dictionaries
            keywords: List of keywords to filter by (optional)
            
        Returns:
            Filtered list of papers
        """
        if not keywords:
            return papers
            
        filtered_papers = []
        for paper in papers:
            title = paper['title'].lower()
            
            # Check if any keyword is in the title
            if any(keyword.lower() in title for keyword in keywords):
                filtered_papers.append(paper)
                
        return filtered_papers
    
    def categorize_paper(self, paper):
        """
        Categorize a paper based on its abstract and title.
        
        Args:
            paper: Paper info dictionary with abstract
            
        Returns:
            Category name (string)
        """
        # Combine title and abstract for better categorization
        text = (paper['title'] + ' ' + paper['abstract']).lower()
        
        # Define category keywords
        category_keywords = {
            "nlp": ["nlp", "language", "text", "transformer", "bert", "gpt", "llm", 
                    "tokenization", "embedding", "translation", "sentiment"],
            "vision": ["vision", "image", "video", "object detection", "segmentation", 
                      "recognition", "cnn", "gan", "diffusion", "generative"],
            "audio": ["audio", "speech", "voice", "sound", "acoustic", "music", 
                     "recognition", "synthesis", "tts", "asr"],
            "reinforcement_learning": ["reinforcement", "rl", "agent", "policy", "reward", 
                                      "q-learning", "dqn", "ppo", "a2c", "mcts"]
        }
        
        # Check each category
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        # Default category if no match
        return "other"
    
    def download_paper(self, paper_info):
        """
        Override download_paper to save to category directories.
        
        Args:
            paper_info: Dictionary with paper information
            
        Returns:
            Updated paper info
        """
        if not paper_info.get('abstract'):
            paper_info = self.get_paper_details(paper_info)
            
        # Get category
        category = self.categorize_paper(paper_info)
        paper_info['category'] = category
        
        # No PDF link available
        if not paper_info.get('pdf_link'):
            print(f"No PDF link found for: {paper_info['title']}")
            return paper_info
            
        # Clean title for filename
        safe_title = re.sub(r'[^\w\s-]', '', paper_info['title'])
        safe_title = re.sub(r'[-\s]+', '_', safe_title).lower()
        
        # Set filenames with position prefix
        position_prefix = f"{paper_info['position']:02d}_"
        pdf_filename = position_prefix + safe_title + '.pdf'
        abstract_filename = position_prefix + safe_title + '.txt'
        
        # Use category-specific paths
        pdf_path = os.path.join(self.papers_dir, category, pdf_filename)
        abstract_path = os.path.join(self.abstracts_dir, category, abstract_filename)
        
        # Download PDF
        print(f"Downloading PDF: {paper_info['title']} (Category: {category})")
        try:
            response = self.session.get(paper_info['pdf_link'], stream=True)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            paper_info['pdf_path'] = pdf_path
            print(f"PDF saved to: {pdf_path}")
            
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            
        # Save abstract
        try:
            with open(abstract_path, 'w', encoding='utf-8') as f:
                f.write(paper_info['abstract'])
                
            paper_info['abstract_path'] = abstract_path
            print(f"Abstract saved to: {abstract_path}")
            
        except Exception as e:
            print(f"Error saving abstract: {e}")
            
        return paper_info
    
    def process_papers(self, limit=10, filter_keywords=None):
        """
        Enhanced processing with filtering.
        
        Args:
            limit: Maximum number of papers to process
            filter_keywords: Keywords for filtering papers (optional)
            
        Returns:
            Processed papers list
        """
        # Get paper links
        papers = self.get_paper_links(limit=limit)
        
        # Apply filtering if keywords provided
        if filter_keywords:
            print(f"Filtering papers with keywords: {filter_keywords}")
            papers = self.filter_papers(papers, filter_keywords)
            
        # Get details and download each paper
        processed_papers = []
        for paper in papers:
            paper_with_details = self.get_paper_details(paper)
            downloaded_paper = self.download_paper(paper_with_details)
            processed_papers.append(downloaded_paper)
            
        # Summarize by category
        categories = {}
        for paper in processed_papers:
            category = paper.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(paper)
            
        print("\nPapers by category:")
        for category, papers in categories.items():
            print(f"\n{category.upper()} ({len(papers)} papers):")
            for paper in papers:
                print(f"  - {paper['title']}")
                
        return processed_papers


if __name__ == "__main__":
    # Example usage
    grabber = CategorizedPaperGrabber()
    
    # Optional: filter papers with specific keywords
    filter_keywords = ["transformer", "diffusion", "llm", "vision"]
    
    # Process papers with filtering
    downloaded_papers = grabber.process_papers(
        limit=20,  # Get more papers initially to ensure we have enough after filtering
        filter_keywords=filter_keywords
    )
    
    print("\nDownload complete! Papers have been categorized and saved.")