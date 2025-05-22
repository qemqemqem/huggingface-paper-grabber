#!/usr/bin/env python3
"""
Filtered HuggingFace Paper Grabber

Downloads papers from HuggingFace's papers page based on abstract filtering.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from paper_filter import should_download


class FilteredPaperGrabber:
    """Paper grabber that filters papers based on abstract content."""
    
    def __init__(self, base_url="https://huggingface.co/papers", 
                 output_dir="filtered_papers"):
        """
        Initialize the filtered paper grabber.
        
        Args:
            base_url: URL to scrape papers from
            output_dir: Directory to save downloaded papers and metadata
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.papers_dir = os.path.join(output_dir, "pdfs")
        self.abstracts_dir = os.path.join(output_dir, "abstracts")
        
        # Create directories if they don't exist
        for directory in [self.output_dir, self.papers_dir, self.abstracts_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # Configure requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_paper_links(self, limit=50):  # Higher initial limit to account for filtering
        """Get links to papers from HuggingFace."""
        print(f"Fetching papers from {self.base_url}...")
        
        response = self.session.get(self.base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find paper articles - updated selector for 2024 website structure
        paper_elements = soup.select('article')
        
        papers = []
        for i, paper_elem in enumerate(paper_elements[:limit]):
            # Extract title
            title_elem = paper_elem.select_one('h3')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            # Extract link to paper page
            link_elem = paper_elem.select_one('a[href^="/papers/"]')
            if not link_elem:
                continue
                
            relative_link = link_elem.get('href')
            paper_url = urljoin(self.base_url, relative_link)
            
            # Get paper ID from URL (e.g., /papers/2505.14683)
            paper_id = relative_link.split("/")[-1]
            
            papers.append({
                'title': title,
                'paper_url': paper_url,
                'paper_id': paper_id,
                'position': i + 1
            })
            
        print(f"Found {len(papers)} papers to analyze")
        return papers
        
    def get_paper_details(self, paper_info):
        """Get abstract and PDF link for a paper."""
        print(f"Fetching details for: {paper_info['title']}")
        
        response = self.session.get(paper_info['paper_url'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract abstract
        abstract = "No abstract available"
        abstract_section = None
        
        # First, try to find a section with "Abstract" header
        for section in soup.select('section'):
            header = section.select_one('h2, h3')
            if header and 'abstract' in header.text.lower():
                abstract_section = section
                break
                
        # If found, extract the text
        if abstract_section:
            # Exclude the header itself
            header = abstract_section.select_one('h2, h3')
            if header:
                header.extract()
                
            abstract = abstract_section.get_text(strip=True)
        else:
            # Fallback: look for common abstract containers
            abstract_elem = soup.select_one('div.paper-abstract, div.abstract, section.abstract')
            if abstract_elem:
                abstract = abstract_elem.get_text(strip=True)
        
        # Extract PDF link
        pdf_link = None
        
        # Option 1: Direct PDF link
        pdf_links = soup.select('a[href$=".pdf"], a[href*="/pdf/"]')
        if pdf_links:
            pdf_link = urljoin(paper_info['paper_url'], pdf_links[0].get('href'))
        
        # Option 2: arXiv ID-based PDF link construction
        if not pdf_link and 'paper_id' in paper_info:
            paper_id = paper_info['paper_id']
            # If it looks like an arXiv ID (e.g., 2505.14683), construct a direct PDF link
            if re.match(r'\d{4}\.\d{5}', paper_id):
                pdf_link = f"https://arxiv.org/pdf/{paper_id}.pdf"
                
        paper_info.update({
            'abstract': abstract,
            'pdf_link': pdf_link
        })
        
        return paper_info
    
    def download_paper(self, paper_info):
        """Download paper PDF and save abstract."""
        if not paper_info.get('pdf_link'):
            print(f"No PDF link found for: {paper_info['title']}")
            return paper_info
            
        # Clean title for filename
        safe_title = re.sub(r'[^\w\s-]', '', paper_info['title'])
        safe_title = re.sub(r'[-\s]+', '_', safe_title).lower()
        
        # Set filenames
        position_prefix = f"{paper_info['position']:02d}_"
        pdf_filename = position_prefix + safe_title + '.pdf'
        abstract_filename = position_prefix + safe_title + '.txt'
        
        pdf_path = os.path.join(self.papers_dir, pdf_filename)
        abstract_path = os.path.join(self.abstracts_dir, abstract_filename)
        
        # Download PDF
        print(f"Downloading PDF: {paper_info['title']}")
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
            
        # Add a small delay to avoid overloading the server
        time.sleep(1)
        
        return paper_info
        
    def process_papers(self, max_downloads=10):
        """
        Main method to process and download papers based on filtering.
        
        Args:
            max_downloads: Maximum number of papers to download after filtering
            
        Returns:
            List of processed paper information
        """
        # Get paper links (with a higher initial limit to allow for filtering)
        initial_limit = max(50, max_downloads * 3)  # Get plenty of candidates
        papers = self.get_paper_links(limit=initial_limit)
        
        # Get details and apply filtering
        filtered_papers = []
        downloaded_count = 0
        
        print(f"\nAnalyzing abstracts to filter papers...")
        
        for paper in papers:
            # Stop if we've reached the max downloads
            if downloaded_count >= max_downloads:
                break
                
            # Get paper details including abstract
            paper_with_details = self.get_paper_details(paper)
            
            # Apply the filter
            if should_download(paper_with_details['abstract'], paper_with_details['title']):
                print(f"✓ Paper accepted: {paper['title']}")
                
                # Download the paper
                downloaded_paper = self.download_paper(paper_with_details)
                filtered_papers.append(downloaded_paper)
                downloaded_count += 1
            else:
                print(f"✗ Paper rejected: {paper['title']}")
            
        print(f"\nDownloaded {downloaded_count} papers after filtering")
        return filtered_papers


if __name__ == "__main__":
    # Example usage
    grabber = FilteredPaperGrabber()
    downloaded_papers = grabber.process_papers(max_downloads=10)
    
    print("\nSummary of downloaded papers:")
    for paper in downloaded_papers:
        print(f"{paper['position']}. {paper['title']}")
        if paper.get('pdf_path'):
            print(f"   PDF: {paper['pdf_path']}")
        if paper.get('abstract_path'):
            print(f"   Abstract: {paper['abstract_path']}")
        print()