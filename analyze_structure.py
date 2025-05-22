#!/usr/bin/env python3
"""Analyzes the structure of the HuggingFace papers page."""

import requests
from bs4 import BeautifulSoup

# Fetch the papers page
print("Fetching https://huggingface.co/papers...")
response = requests.get("https://huggingface.co/papers")
soup = BeautifulSoup(response.text, "html.parser")

# Print basic info
print(f"Page title: {soup.title.text}")
print(f"Status code: {response.status_code}")

# Check for paper container
paper_grid = soup.find("div", class_="papers-grid")
print(f"Paper grid found: {paper_grid is not None}")

# Look for paper cards
paper_cards = soup.select("div.paper-card")
print(f"Paper cards found: {len(paper_cards)}")

# Look for other possible containers
print("\nPossible paper containers:")
for tag in soup.find_all(["div", "article"], class_=True)[:15]:
    print(f"- {tag.name} with class {tag.get('class')}")

# Print first paper if found
if paper_cards:
    print("\nFirst paper HTML:")
    print(paper_cards[0].prettify())
else:
    print("\nNo paper cards found with current selector.")
    print("Trying to find paper links...")
    
    # Look for hrefs that might be paper links
    paper_links = soup.select("a[href*='/papers/']")
    print(f"Found {len(paper_links)} potential paper links")
    
    if paper_links:
        for i, link in enumerate(paper_links[:5]):
            print(f"\nPaper link {i+1}:")
            print(f"URL: {link.get('href')}")
            print(f"Text: {link.get_text().strip()}")
            print(f"Parent: {link.parent.name} with class {link.parent.get('class')}")
            
        # Try to get a full paper container
        first_paper = paper_links[0].find_parent("div")
        if first_paper:
            print("\nFirst paper container:")
            print(first_paper.prettify()[:500])