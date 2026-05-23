#!/usr/bin/env python3
"""
RecordsReveal AI-Driven Investigation
Two-phase approach:
  Phase 1 (Ollama): Comprehensive data analysis - FREE
  Phase 2 (Claude): Investigative journalism writing - ~$0.02-0.08
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Import helper functions
from ollama_helper import ask_ollama_code, test_connection
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install anthropic python-dotenv pandas")
    sys.exit(1)

# Load Claude API key
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print(f"❌ ANTHROPIC_API_KEY not found in {env_path}")
    print("\nCreate a .env file with:")
    print("ANTHROPIC_API_KEY=sk-ant-...")
    sys.exit(1)

client = Anthropic(api_key=api_key)

def ask_claude(prompt, model="claude-sonnet-4-5-20250929"):
    """Send prompt to Claude API"""
    models_to_try = [
        "claude-sonnet-4-5-20250929",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620"
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            message = client.messages.create(
                model=model_name,
                max_tokens=4000,
                temperature=1,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            last_error = e
            if "not_found_error" in str(e):
                continue
            else:
                break
    
    print(f"❌ Claude API error: {last_error}")
    return None

def phase1_ollama_analysis(csv_path):
    """
    Phase 1: Ollama performs comprehensive data analysis
    Cost: $0.00 (local/remote Ollama)
    """
    print("\n" + "="*70)
    print("🔬 PHASE 1: OLLAMA DATA ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print("Model: qwen2.5-coder:7b (code execution)")
    print("Cost: $0.00")
    print("="*70 + "\n")
    
    # Test Ollama connection
    print("📡 Testing Ollama connection...")
    if not test_connection():
        print("\n❌ Cannot connect to Ollama. Exiting.")
        sys.exit(1)
    
    # Load dataset for basic info
    print(f"\n📂 Loading dataset...")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns\n")
    
    # Create comprehensive analysis prompt for Ollama
    ollama_prompt = f"""You are a data analyst. Analyze this dataset and provide comprehensive statistics.

DATASET: {csv_path}
ROWS: {len(df):,}
COLUMNS: {df.columns.tolist()}

SAMPLE DATA (first 3 rows):
{df.head(3).to_string()}

COLUMN TYPES:
{df.dtypes.to_string()}

Please analyze and return a structured summary in this EXACT format:

## DATASET OVERVIEW
- Rows: [number]
- Columns: [number]
- Date range: [if temporal data exists]

## NUMERICAL COLUMNS
For each numeric column, provide:
- Mean, Median, Min, Max
- Outliers (values > 2 std devs from mean)
- Distribution notes

## CATEGORICAL COLUMNS
For each categorical column:
- Unique values count
- Top 5 most frequent values with counts
- Any rare categories worth noting

## KEY PATTERNS
- Correlations between columns (if numeric data)
- Unexpected relationships
- Clusters or natural groupings (if you see them)
- Anomalies or suspicious data points

## MOST NEWSWORTHY FINDINGS
List the 3-5 most surprising or significant patterns you found.
What would make a journalist say "Wow, I need to write about this"?

Be specific with numbers. Focus on patterns that contradict expectations or reveal disparities."""

    print("🤖 Ollama analyzing data (this may take 30-60 seconds)...")
    analysis = ask_ollama_code(ollama_prompt, model="qwen2.5-coder:7b")
    
    if not analysis:
        print("❌ Ollama analysis failed")
        return None
    
    print("\n✅ Ollama analysis complete!\n")
    print("="*70)
    print("📊 OLLAMA ANALYSIS SUMMARY")
    print("="*70)
    print(analysis[:1000] + "..." if len(analysis) > 1000 else analysis)
    print("="*70 + "\n")
    
    return {
        "dataset": csv_path,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample_data": df.head(5).to_dict(),
        "ollama_analysis": analysis
    }

def phase2_claude_journalism(data_analysis):
    """
    Phase 2: Claude writes investigative journalism
    Cost: ~$0.02-0.08 (Claude API)
    """
    print("\n" + "="*70)
    print("✍️  PHASE 2: CLAUDE INVESTIGATIVE JOURNALISM")
    print("="*70)
    print("Model: claude-sonnet-4-5-20250929")
    print("Cost: ~$0.02-0.08")
    print("="*70 + "\n")
    
    # Build comprehensive prompt for Claude
    claude_prompt = f"""You are an investigative data journalist for RecordsReveal, a data journalism publication known for bold, specific, number-driven stories.

# DATASET ANALYSIS
You just received comprehensive analysis from your data team. Here's what they found:

{data_analysis['ollama_analysis']}

DATASET: {data_analysis['dataset']}
RECORDS: {data_analysis['rows']:,}

# YOUR MISSION
Write a compelling data investigation. You have COMPLETE CREATIVE FREEDOM.

# RECORDSREVEAL STYLE GUIDE

**Tone:**
- Direct, conversational, immediate
- Use "you" to make it personal
- Present tense for impact
- Contradict conventional wisdom when possible

**Numbers:**
- Always use **bold** for key numbers: **$829 million**, **65.4%**, **1,024 transactions**
- Be specific: not "many" but "242 districts"
- Lead with the most surprising number

**Structure:**
- Headline: 12-25 words, dramatic, uses specific numbers
- Lede: 3-5 sentences that challenge assumptions and reveal findings
  - Start with relatable scenario
  - Contradict conventional wisdom
  - Use specific numbers and times
  - Make it immediate and personal

- Findings: As many as you need (NOT forced to 3-4)
  - Each finding should reveal ONE major pattern
  - Start with impact: "This is the finding that..."
  - Use 2-3 paragraphs per finding
  - Bold all key numbers
  - Explain WHY this matters to readers

**Examples of Good RecordsReveal Headlines:**
- "1 in 5 NYC Crashes Involve Driver Distraction. Phones Are the New Drunk Driving."
- "$829 Million in Dark Money Flooded Swing Districts. We Analyzed 242 Races to Find Who's Really Buying Your Vote."
- "5:00 PM Is NYC's Most Dangerous Hour. Here's Why Rush Hour Kills."

**Examples of Good RecordsReveal Lede:**
"If you live in New York City and drive home at 5:00 PM on a weekday, you are statistically entering the most dangerous hour of your entire week. Not 2:00 AM when the drunk drivers are out. Not rush hour in the morning. 5:00 PM."

"If you believe your vote is swayed by the candidate who knocks on your door or the debate you watched last Tuesday night, consider this: in Colorado's 8th district alone, shadow groups you've never heard of spent **$24.6 million**—roughly $127 for every single voter—to change your mind."

# WHAT TO FOCUS ON
- What's most SURPRISING in the data?
- What contradicts what people THINK they know?
- What reveals DISPARITY or INJUSTICE?
- What would make someone FORWARD this article?
- What matters to REGULAR PEOPLE (not just data nerds)?

# OUTPUT FORMAT
Return ONLY valid JSON (no markdown, no explanations):

{{
  "headline": "Your compelling headline here",
  "lede": "Your gripping 3-5 sentence lede here",
  "findings": [
    {{
      "title": "Finding Title",
      "body": "Full markdown text with **bold numbers**. Multiple paragraphs separated by \\n\\n. Explain the pattern, why it matters, what it means for readers.",
      "key_stat": "One big number to display (e.g., '$24.6M' or '65.4%')"
    }}
  ],
  "pull_quotes": [
    "Compelling 10-20 word quote that highlights surprising finding",
    "Another quotable insight with a number"
  ],
  "methodology": "Brief 2-3 sentence explanation of the analysis performed (reference Ollama's statistical analysis)",
  "stat_boxes": [
    {{
      "label": "Short label",
      "value": "Big number with units",
      "context": "Brief explanatory text"
    }}
  ]
}}

CRITICAL: Return ONLY the JSON. No explanations before or after.
Be bold. Be specific. Find the story that matters."""

    print("🤖 Claude writing investigation...")
    response = ask_claude(claude_prompt)
    
    if not response:
        print("❌ Claude journalism failed")
        return None
    
    # Parse JSON response
    try:
        # Clean up response (remove markdown if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        investigation = json.loads(response)
        
        print("\n✅ Claude investigation complete!\n")
        print("="*70)
        print("📰 INVESTIGATION PREVIEW")
        print("="*70)
        print(f"Headline: {investigation['headline']}")
        print(f"Findings: {len(investigation.get('findings', []))}")
        print(f"Pull Quotes: {len(investigation.get('pull_quotes', []))}")
        print(f"Stat Boxes: {len(investigation.get('stat_boxes', []))}")
        print("="*70 + "\n")
        
        return investigation
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Claude response as JSON: {e}")
        print(f"\nResponse preview:\n{response[:500]}...")
        return None

def investigate(csv_path, output_dir="investigation_output"):
    """
    Main investigation workflow
    """
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*15 + "RECORDSREVEAL AI INVESTIGATION" + " "*23 + "║")
    print("╚"+"═"*68+"╝")
    
    start_time = datetime.now()
    
    # Validate input
    if not os.path.exists(csv_path):
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Phase 1: Ollama Analysis (FREE)
    data_analysis = phase1_ollama_analysis(csv_path)
    if not data_analysis:
        return None
    
    # Phase 2: Claude Journalism (~$0.02-0.08)
    investigation = phase2_claude_journalism(data_analysis)
    if not investigation:
        return None
    
    # Combine results
    output = {
        "generated_at": datetime.now().isoformat(),
        "dataset": csv_path,
        "data_analysis": data_analysis,
        **investigation
    }
    
    # Save investigation JSON
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_dir, f"investigation-{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*23 + "✅ INVESTIGATION COMPLETE" + " "*20 + "║")
    print("╚"+"═"*68+"╝\n")
    print(f"📁 Output: {output_file}")
    print(f"⏱️  Time: {elapsed:.0f} seconds")
    print(f"💰 Cost: ~$0.02-0.08 (Claude journalism only)")
    print(f"\n📰 Headline: {investigation['headline'][:80]}...")
    print(f"📊 Findings: {len(investigation.get('findings', []))}")
    print(f"💬 Pull Quotes: {len(investigation.get('pull_quotes', []))}")
    
    print("\n" + "─"*70)
    print("NEXT STEP: Render to HTML")
    print("─"*70)
    print(f"  python3 render.py {output_file}\n")
    
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python investigate.py <csv_file> [output_dir]")
        print("\nExample:")
        print("  python investigate.py data/campaign_finance/dark_money.csv")
        print("\nThis will:")
        print("  1. Use Ollama to analyze data (FREE)")
        print("  2. Use Claude to write investigation (~$0.02-0.08)")
        print("  3. Output investigation JSON")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "investigation_output"
    
    investigate(csv_path, output_dir)

if __name__ == "__main__":
    main()
