"""
Ollama Helper for RecordsReveal
Connects to remote Ollama server for cost-free AI operations
"""

import requests
import json

OLLAMA_HOST = "http://192.168.1.153:11434"

def test_connection():
    """Test if Ollama server is accessible"""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if r.status_code == 200:
            models = r.json().get("models", [])
            print(f"✅ Connected to Ollama server at {OLLAMA_HOST}")
            print(f"Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"❌ Ollama server returned status {r.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama server: {e}")
        return False

def ask_ollama_code(prompt, model="qwen2.5-coder:7b"):
    """
    Use qwen2.5-coder:7b for code tasks
    - Code generation
    - Debugging assistance
    - Data analysis code
    """
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        print(f"Error calling Ollama (code): {e}")
        return None

def ask_ollama_write(prompt, model="llama3.2"):
    """
    Use llama3.2 for writing tasks
    - Finding insights
    - Generating headlines
    - Writing article prose
    - Creating pull quotes
    """
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        print(f"Error calling Ollama (write): {e}")
        return None

def ask_ollama_eda_insights(eda_summary):
    """
    Extract surprising insights from EDA results
    Used in Phase 2 of investigation workflow
    """
    prompt = f"""You are a data journalist. I just ran exploratory data analysis on a dataset.

Here's what I found:
{eda_summary}

Please identify:
1. The most surprising or newsworthy finding
2. Any unexpected patterns or anomalies
3. What questions this data raises

Keep your response concise and journalistic (2-3 sentences per point)."""
    
    return ask_ollama_write(prompt)

def ask_ollama_cluster_names(cluster_summaries):
    """
    Generate descriptive names for data clusters
    Used in Phase 4 of investigation workflow
    """
    prompt = f"""You are naming clusters from a K-Means analysis for a data journalism investigation.

Here are the cluster characteristics:
{cluster_summaries}

For each cluster, provide:
1. A short descriptive name (2-4 words)
2. One sentence explaining what makes this cluster distinct

Format as JSON."""
    
    return ask_ollama_write(prompt)

def ask_ollama_headline(findings, dataset_context):
    """
    Generate compelling headlines using journalism formulas
    Used in Phase 8 of investigation workflow
    """
    prompt = f"""You are a data journalist writing headlines for a RecordsReveal investigation.

Dataset context: {dataset_context}

Key findings:
{findings}

Generate 3 headline options using these formulas:
1. NUMBER + SHOCKING FACT (e.g., "1 in 5 Crashes Involve Distracted Drivers")
2. GEOGRAPHIC + SUPERLATIVE (e.g., "Brooklyn Leads NYC in Pedestrian Accidents")
3. TIME-BASED PATTERN (e.g., "Crashes Spike During Rush Hour, Data Shows")

Keep each headline under 60 characters."""
    
    return ask_ollama_write(prompt)

def ask_ollama_pull_quotes(article_text):
    """
    Extract compelling pull quotes from article text
    Used in Phase 8 of investigation workflow
    """
    prompt = f"""Extract 2-3 compelling pull quotes from this investigation article.

Article:
{article_text}

Pull quotes should be:
- 10-20 words max
- Self-contained (make sense out of context)
- Highlight the most surprising findings
- Sound authoritative and journalistic

Return just the quotes, one per line."""
    
    return ask_ollama_write(prompt)

def ask_ollama_social_posts(headline, key_finding, url):
    """
    Generate social media posts for investigation
    Used in Phase 10 of investigation workflow
    """
    prompt = f"""Generate social media posts for this data investigation:

Headline: {headline}
Key Finding: {key_finding}
URL: {url}

Create:
1. Twitter post (280 chars max, include hashtags)
2. LinkedIn post (professional tone, 2-3 sentences)
3. Facebook post (conversational tone, includes question for engagement)

Format as JSON."""
    
    return ask_ollama_write(prompt)

if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing Ollama connection...")
    test_connection()
    
    print("\nTesting code model (qwen2.5-coder:7b)...")
    response = ask_ollama_code("Write a Python function to calculate the mean of a list.")
    if response:
        print(f"Response preview: {response[:200]}...")
    
    print("\nTesting writing model (llama3.2)...")
    response = ask_ollama_write("Write a one-sentence headline about traffic crashes in NYC.")
    if response:
        print(f"Response: {response}")
