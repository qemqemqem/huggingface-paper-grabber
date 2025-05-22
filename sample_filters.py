#!/usr/bin/env python3
"""
Sample filters for HuggingFace Paper Grabber.

This module contains example filter functions that can be used
to select papers based on their abstract content.
"""


def should_download(abstract, title=""):
    """
    Determine if a paper should be downloaded based on AI topics.
    
    This is an example filter that checks for AI-related terms.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str, optional): The title of the paper
        
    Returns:
        bool: True if the paper is about AI and meets criteria
    """
    # Convert to lowercase for case-insensitive matching
    text = (abstract + " " + title).lower()
    
    # Example: Only download papers about specific AI topics
    ai_topics = [
        "large language model", "llm", "transformer", 
        "deep learning", "neural network", "reinforcement learning"
    ]
    
    # Check if any AI topic is present
    has_ai_topic = any(topic in text for topic in ai_topics)
    
    # Additional criteria could be added here
    # For example: paper should be recent, technical, etc.
    
    return has_ai_topic


def ml_focus_filter(abstract, title=""):
    """
    Filter specifically for machine learning papers.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str, optional): The title of the paper
        
    Returns:
        bool: True if the paper focuses on machine learning
    """
    text = (abstract + " " + title).lower()
    
    # Core ML terms
    ml_terms = [
        "machine learning", "supervised learning", "unsupervised learning",
        "classification", "regression", "clustering", "neural network",
        "deep learning", "feature extraction", "training", "model"
    ]
    
    # Check if multiple ML terms are present (indicating focus)
    ml_term_count = sum(1 for term in ml_terms if term in text)
    
    # Return True if at least 2 ML terms are present
    return ml_term_count >= 2


def nlp_only_filter(abstract, title=""):
    """
    Filter for papers focusing on natural language processing.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str, optional): The title of the paper
        
    Returns:
        bool: True if the paper is about NLP
    """
    text = (abstract + " " + title).lower()
    
    # NLP-specific terms
    nlp_terms = [
        "language model", "nlp", "natural language", "text", "token", 
        "word embedding", "sentiment", "translation", "named entity",
        "transformer", "bert", "gpt", "llm", "large language model"
    ]
    
    # Check if any NLP term is present
    return any(term in text for term in nlp_terms)


def vision_only_filter(abstract, title=""):
    """
    Filter for papers focusing on computer vision.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str, optional): The title of the paper
        
    Returns:
        bool: True if the paper is about computer vision
    """
    text = (abstract + " " + title).lower()
    
    # Vision-specific terms
    vision_terms = [
        "computer vision", "image", "visual", "object detection",
        "segmentation", "recognition", "cnn", "convolutional neural network",
        "gan", "generative adversarial", "diffusion", "video"
    ]
    
    # Check if any vision term is present
    return any(term in text for term in vision_terms)