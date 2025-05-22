#!/usr/bin/env python3
"""
HuggingFace Paper Grabber

Downloads papers from HuggingFace's papers page along with their abstracts.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


class HFPaperGrabber:
    """Main class for grabbing papers from HuggingFace."""
    
    def __init__(self, base_url="https://huggingface.co/papers", 
                 output_dir="downloaded_papers"):
        """
        Initialize the HuggingFace paper grabber.
        
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
    
    def get_paper_links(self, limit=10):
        """
        Get links to the top papers.
        
        Args:
            limit: Maximum number of papers to retrieve
            
        Returns:
            List of dictionaries containing paper information
        """
        print(f"Fetching papers from {self.base_url}...")
        
        response = self.session.get(self.base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        paper_elements = soup.select('.paper-card')
        
        papers = []
        for i, paper_elem in enumerate(paper_elements[:limit]):
            # Extract title
            title_elem = paper_elem.select_one('.paper-title')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract link to paper page
            link_elem = paper_elem.select_one('a')
            relative_link = link_elem.get('href') if link_elem else None
            if not relative_link:
                continue
                
            paper_url = urljoin(self.base_url, relative_link)
            
            papers.append({
                'title': title,
                'paper_url': paper_url,
                'position': i + 1
            })
            
        return papers
        
    def get_paper_details(self, paper_info):
        """
        Get details about a specific paper including abstract and PDF link.
        
        Args:
            paper_info: Dictionary containing paper information
            
        Returns:
            Updated paper info dictionary with abstract and PDF link
        """
        print(f"Fetching details for: {paper_info['title']}")
        
        response = self.session.get(paper_info['paper_url'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract abstract
        abstract_elem = soup.select_one('.paper-abstract')
        abstract = abstract_elem.text.strip() if abstract_elem else "No abstract available"
        
        # Extract PDF link
        pdf_link = None
        for link in soup.select('a'):
            href = link.get('href')
            if href and (href.endswith('.pdf') or '/pdf/' in href):
                pdf_link = urljoin(paper_info['paper_url'], href)
                break
                
        paper_info.update({
            'abstract': abstract,
            'pdf_link': pdf_link
        })
        
        return paper_info
    
    def download_paper(self, paper_info):
        """
        Download a paper's PDF and save its abstract.
        
        Args:
            paper_info: Dictionary containing paper information
            
        Returns:
            Updated paper info with local file paths
        """
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
        
    def process_papers(self, limit=10):
        """
        Main method to process and download papers.
        
        Args:
            limit: Maximum number of papers to process
            
        Returns:
            List of processed paper information
        """
        # Get paper links
        papers = self.get_paper_links(limit=limit)
        
        # Get details and download each paper
        processed_papers = []
        for paper in papers:
            paper_with_details = self.get_paper_details(paper)
            downloaded_paper = self.download_paper(paper_with_details)
            processed_papers.append(downloaded_paper)
            
        return processed_papers


if __name__ == "__main__":
    # Example usage
    grabber = HFPaperGrabber()
    downloaded_papers = grabber.process_papers(limit=10)
    
    print("\nSummary of downloaded papers:")
    for paper in downloaded_papers:
        print(f"{paper['position']}. {paper['title']}")
        if paper.get('pdf_path'):
            print(f"   PDF: {paper['pdf_path']}")
        if paper.get('abstract_path'):
            print(f"   Abstract: {paper['abstract_path']}")
        print()