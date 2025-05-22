#!/usr/bin/env python3
"""
LLM-based paper filter using LiteLLM.

This module uses an LLM (Claude 3.7) to evaluate papers based on their abstracts
and a custom criteria prompt.
"""

import json
import os
import sys
import litellm

# Configure LiteLLM to use Claude 3.7
litellm.set_verbose = False


def load_criteria_prompt(prompt_file="what_makes_a_good_paper.txt"):
    """Load the criteria prompt from a file."""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading criteria prompt: {e}")
        sys.exit(1)


def create_evaluation_prompt(abstract, title, criteria):
    """Create the full prompt for the LLM."""
    return f"""
You are an expert research paper evaluator. Your task is to evaluate a research paper based on its abstract and title according to specific criteria.

# Paper Information
Title: {title}
Abstract: {abstract}

# Evaluation Criteria
{criteria}

# Instructions
Based on the abstract and title, evaluate whether this paper meets the criteria.
Provide your evaluation in a structured JSON format with the following fields:
1. "should_download" (boolean): true if the paper should be downloaded, false otherwise
2. "relevance_score" (integer, 1-10): rate the paper's relevance to the criteria on a scale of 1-10
3. "reasoning" (string): brief explanation for your evaluation

Output ONLY valid JSON without any additional text, comments, or markdown formatting.
"""


def evaluate_paper_with_llm(abstract, title="", model="claude-3-7-sonnet", prompt_file="what_makes_a_good_paper.txt"):
    """
    Evaluate a paper using LiteLLM and Claude 3.7.
    
    Args:
        abstract (str): The paper abstract
        title (str): The paper title
        model (str): LLM model to use
        prompt_file (str): File containing evaluation criteria
        
    Returns:
        dict: Evaluation results with should_download, relevance_score, and reasoning
    """
    # Load criteria
    criteria = load_criteria_prompt(prompt_file)
    
    # Create the full prompt
    prompt = create_evaluation_prompt(abstract, title, criteria)
    
    try:
        # Call the LLM
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for more consistent evaluations
            max_tokens=500
        )
        
        # Extract and parse the response
        result_text = response.choices[0].message.content.strip()
        
        try:
            # Parse JSON response
            result = json.loads(result_text)
            
            # Ensure required fields are present
            if "should_download" not in result or "relevance_score" not in result:
                print(f"Warning: LLM response missing required fields: {result}")
                # Provide default values if missing
                result["should_download"] = result.get("should_download", False)
                result["relevance_score"] = result.get("relevance_score", 1)
                result["reasoning"] = result.get("reasoning", "Incomplete LLM response")
                
            return result
            
        except json.JSONDecodeError:
            print(f"Error: LLM did not return valid JSON. Response: {result_text}")
            # Return default values on error
            return {
                "should_download": False,
                "relevance_score": 1,
                "reasoning": "Failed to parse LLM response as JSON"
            }
            
    except Exception as e:
        print(f"Error during LLM evaluation: {e}")
        # Return default values on error
        return {
            "should_download": False,
            "relevance_score": 1,
            "reasoning": f"LLM evaluation error: {str(e)}"
        }


# The main filter function expected by the paper grabber
def should_download(abstract, title=""):
    """
    Determine if a paper should be downloaded based on LLM evaluation.
    
    Args:
        abstract (str): The abstract text of the paper
        title (str): The title of the paper
        
    Returns:
        bool: True if the paper should be downloaded, False otherwise
    """
    # Get the full evaluation
    evaluation = evaluate_paper_with_llm(abstract, title)
    
    # Print the evaluation for transparency
    print(f"LLM evaluation:")
    print(f"  Relevance score: {evaluation['relevance_score']}/10")
    print(f"  Reasoning: {evaluation['reasoning']}")
    
    # Return the boolean decision
    return evaluation["should_download"]


# Test function to demonstrate the filter
if __name__ == "__main__":
    # Example abstract
    test_abstract = """
    We present a novel approach to reinforcement learning in multi-agent systems,
    specifically examining how macaque monkeys and other primates develop collaborative
    strategies. Our model demonstrates significant improvements over baseline approaches,
    with implications for both artificial intelligence and evolutionary biology.
    """
    
    test_title = "Primate-Inspired Collaborative Learning in Multi-Agent Systems"
    
    # Run the evaluation
    result = evaluate_paper_with_llm(test_abstract, test_title)
    
    # Print results
    print("\nTest Evaluation Results:")
    print(json.dumps(result, indent=2))
    print(f"\nShould download: {should_download(test_abstract, test_title)}")