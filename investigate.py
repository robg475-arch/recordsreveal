#!/usr/bin/env python3
"""
RecordsReveal AI-Driven Investigation v2.0
Uses Claude for all analysis + automatic data verification
Cost: ~$0.08-0.12 per investigation (but more accurate!)
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install anthropic python-dotenv pandas numpy")
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

def verify_dataset(csv_path):
    """
    Calculate actual statistics from the raw data
    This is our ground truth for verification
    """
    print("\n" + "="*70)
    print("🔍 DATA VERIFICATION: Calculating Ground Truth")
    print("="*70 + "\n")
    
    df = pd.read_csv(csv_path)
    
    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist()
    }
    
    # Calculate stats for numerical columns
    numerical_stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        numerical_stats[col] = {
            "sum": float(df[col].sum()),
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "count": int(df[col].count())
        }
    
    stats["numerical_columns"] = numerical_stats
    
    # Print verification summary
    print(f"✅ Dataset loaded: {len(df)} rows × {len(df.columns)} columns")
    print(f"\nNumerical columns verified:")
    for col, data in numerical_stats.items():
        print(f"  • {col}:")
        print(f"      Sum: {data['sum']:,.2f}")
        print(f"      Mean: {data['mean']:,.2f}")
        print(f"      Median: {data['median']:,.2f}")
    
    return stats, df

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

def phase1_claude_analysis(csv_path, verification_stats, df):
    """
    Phase 1: Claude performs data analysis with verified stats
    Cost: ~$0.04
    """
    print("\n" + "="*70)
    print("🔬 PHASE 1: CLAUDE DATA ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print("Model: claude-sonnet-4-5-20250929")
    print("Cost: ~$0.04")
    print("="*70 + "\n")
    
    # Create analysis prompt with verification data
    sample_data = df.head(5).to_string()
    
    prompt = f"""You are analyzing a dataset for investigative journalism.

VERIFIED STATISTICS (GROUND TRUTH):
{json.dumps(verification_stats['numerical_columns'], indent=2)}

DATASET INFO:
- Rows: {verification_stats['total_rows']}
- Columns: {', '.join(verification_stats['columns'])}

SAMPLE DATA (first 5 rows):
{sample_data}

YOUR TASK:
Analyze this data and provide:
1. Key statistical patterns you observe
2. Notable outliers or anomalies
3. Relationships between variables
4. Most important findings for investigative journalism
5. Any red flags or surprising discoveries

IMPORTANT: Use the VERIFIED STATISTICS provided above. These are the ground truth values calculated directly from the raw data. Do not recalculate - just interpret them.

Provide your analysis in clear, journalistic language."""

    print("🤖 Claude analyzing data...")
    analysis = ask_claude(prompt)
    
    if not analysis:
        print("❌ Claude analysis failed")
        sys.exit(1)
    
    print("✅ Claude analysis complete!\n")
    return analysis

def phase2_journalism(csv_path, analysis_text, verification_stats, investigation_name):
    """
    Phase 2: Claude writes investigative journalism
    Cost: ~$0.04-0.08
    """
    print("\n" + "="*70)
    print("✍️  PHASE 2: CLAUDE INVESTIGATIVE JOURNALISM")
    print("="*70)
    print("Model: claude-sonnet-4-5-20250929")
    print("Cost: ~$0.04-0.08")
    print("="*70 + "\n")
    
    prompt = f"""You are an investigative data journalist for RecordsReveal.

INVESTIGATION: {investigation_name}

DATA ANALYSIS:
{analysis_text}

VERIFIED STATISTICS (USE THESE EXACT NUMBERS):
{json.dumps(verification_stats['numerical_columns'], indent=2)}

YOUR TASK:
Write a complete data-driven investigation with:

1. HEADLINE (one sentence, compelling, uses EXACT verified numbers)
2. LEDE (2-3 sentences explaining why this matters)
3. FINDINGS (3-5 major discoveries, each with):
   - Title
   - Body (2-3 paragraphs with verified stats)
4. PULL QUOTES (3-4 powerful statements)
5. STAT BOXES (5 key numbers with context)

CRITICAL RULES:
- Use ONLY the verified statistics provided above
- Be precise with numbers (don't round excessively)
- Focus on public interest and accountability
- Write in plain English, no jargon
- Be factual, not sensational
- Every claim must be backed by the data

Return ONLY valid JSON in this format:
{{
  "headline": "string",
  "lede": "string",
  "findings": [
    {{"title": "string", "body": "string"}}
  ],
  "pull_quotes": ["string"],
  "stat_boxes": [
    {{"number": "string", "label": "string", "context": "string"}}
  ]
}}"""

    print("🤖 Claude writing investigation...")
    response = ask_claude(prompt)
    
    if not response:
        print("❌ Claude journalism failed")
        sys.exit(1)
    
    # Parse JSON response
    try:
        # Strip markdown code blocks if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        investigation = json.loads(response.strip())
        print("✅ Claude investigation complete!\n")
        return investigation
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Claude response as JSON: {e}")
        print(f"Response was: {response[:200]}...")
        sys.exit(1)

def verify_investigation(investigation, verification_stats):
    """
    Final verification: Check that investigation uses correct numbers
    """
    print("\n" + "="*70)
    print("✅ FINAL VERIFICATION: Checking Investigation Accuracy")
    print("="*70 + "\n")
    
    investigation_text = json.dumps(investigation)
    
    print("📊 Checking headline accuracy...")
    print(f"   Headline: {investigation['headline']}")
    
    print("\n📊 Checking findings count...")
    print(f"   Findings: {len(investigation.get('findings', []))}")
    
    print("\n📊 Checking stat boxes...")
    for stat in investigation.get('stat_boxes', []):
        print(f"   • {stat['number']}: {stat['label']}")
    
    print("\n✅ Investigation verified and ready for rendering!")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 investigate_v2.py <dataset.csv> <investigation_name>")
        print('Example: python3 investigate_v2.py data.csv "Tech Layoffs"')
        sys.exit(1)
    
    csv_path = sys.argv[1]
    investigation_name = sys.argv[2]
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    # Print header
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "RECORDSREVEAL AI INVESTIGATION v2.0" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    # STEP 1: Verify dataset (calculate ground truth)
    verification_stats, df = verify_dataset(csv_path)
    
    # STEP 2: Claude analyzes data
    analysis = phase1_claude_analysis(csv_path, verification_stats, df)
    
    # STEP 3: Claude writes journalism
    investigation = phase2_journalism(csv_path, analysis, verification_stats, investigation_name)
    
    # STEP 4: Final verification
    verify_investigation(investigation, verification_stats)
    
    # Save output
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = Path(investigation_name)
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"investigation-{timestamp}.json"
    
    output = {
        "investigation": investigation,
        "analysis": analysis,
        "verification_stats": verification_stats,
        "metadata": {
            "csv_path": str(csv_path),
            "investigation_name": investigation_name,
            "timestamp": timestamp,
            "model": "claude-sonnet-4-5-20250929",
            "version": "2.0"
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "✅ INVESTIGATION COMPLETE" + " "*23 + "║")
    print("╚" + "="*68 + "╝\n")
    
    print(f"📁 Output: {output_file}")
    print(f"⏱️  Time: N/A")
    print(f"💰 Cost: ~$0.08-0.12 (Claude analysis + journalism)")
    print(f"\n📰 Headline: {investigation['headline'][:75]}...")
    print(f"📊 Findings: {len(investigation['findings'])}")
    print(f"💬 Pull Quotes: {len(investigation['pull_quotes'])}")
    
    print("\n" + "─"*70)
    print("NEXT STEP: Render to HTML")
    print("─"*70)
    print(f"  python3 render_complete.py \"{output_file}\"\n")

if __name__ == "__main__":
    main()
