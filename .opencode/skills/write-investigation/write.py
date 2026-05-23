#!/usr/bin/env python3
"""
RecordsReveal Write Investigation Skill
Generates journalism prose from analysis insights using Claude API
"""

import sys
import os
import json
from pathlib import Path

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install anthropic python-dotenv")
    sys.exit(1)

# Load API key from .env
# Find .env file in project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
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
    # Try multiple models in order
    models_to_try = [
        "claude-sonnet-4-5-20250929",   # Latest Sonnet 4.5 (same as OpenCode)
        "claude-3-5-sonnet-20241022",   # Latest Sonnet 3.5
        "claude-3-5-sonnet-20240620"    # Older Sonnet 3.5
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            message = client.messages.create(
                model=model_name,
                max_tokens=2000,
                temperature=1,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            last_error = e
            if "not_found_error" in str(e):
                continue  # Try next model
            else:
                break  # Different error, don't retry
    
    print(f"❌ Claude API error: {last_error}")
    return None


def ask_claude_old(prompt, model="claude-sonnet-4-20250514"):
    """Send prompt to Claude API"""
    try:
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=1,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return None


def write_investigation(combined_insights_path, page_data_path, output_dir="analysis_results", use_claude=True):
    """
    Generate article content from analysis insights
    """
    print("\n" + "="*70)
    print("✍️  RECORDSREVEAL WRITE INVESTIGATION")
    print("="*70)
    print(f"Insights: {combined_insights_path}")
    print(f"Page data: {page_data_path}")
    print(f"AI: Claude API (Sonnet 4)")
    print("="*70 + "\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load inputs
    print(f"📂 Loading inputs...")
    with open(combined_insights_path) as f:
        combined = json.load(f)
    with open(page_data_path) as f:
        page_data = json.load(f)
    
    print(f"✅ Loaded insights from {len(combined.get('analyses', []))} analyses\n")
    
    article = {
        "dataset": combined.get("dataset", "Unknown"),
        "analyses_used": combined.get("analyses", []),
        "headline": "",
        "lede": "",
        "findings": [],
        "pull_quotes": [],
        "methodology": ""
    }
    
    # Extract key stats for article
    stats = page_data.get("stats", {})
    
    print("="*70)
    print("📰 GENERATING HEADLINE")
    print("="*70 + "\n")
    
    # Generate headline
    headline_prompt = f"""You are writing a headline for RecordsReveal, an investigative data journalism site.

Dataset: {article['dataset']}
Key findings:
- Total records: {stats.get('total_records', 'N/A')}
- Peak time: {stats.get('peak_hour', 'N/A')}
- Top location: {stats.get('top_location', 'N/A')} ({stats.get('top_location_count', 'N/A')} records)
- Majority category: {stats.get('majority_category', 'N/A')} ({stats.get('majority_pct', 'N/A')})
- Top entity: {stats.get('top_entity', 'N/A')} ({stats.get('top_entity_amount', 'N/A')})
- Total financial: {stats.get('total_financial', 'N/A')}
- Comparative advantage: {stats.get('comparative_advantage', 'N/A')} ({stats.get('comparative_leader', 'N/A')})
- Attack ads: {stats.get('pct_attack', 'N/A')} of spending
- Dominant spender: {stats.get('dominant_spender', 'N/A')} ({stats.get('dominant_spender_amount', 'N/A')})
- Top 10 concentration: {stats.get('top_10_pct', 'N/A')}
- Top state: {stats.get('top_state', 'N/A')} ({stats.get('top_state_amount', 'N/A')})
- Micro-targeting: {stats.get('micro_target_entity', 'N/A')} ({stats.get('micro_target_transactions', 'N/A')} transactions)

Write a compelling headline using one of these proven formulas:

Formula A: "[Specific time/location] [becomes/reveals] [dramatic outcome]. We analyzed [N] [records] to find out why."
Example: "Every weekday at 5:00 PM, New York City's roads become a battlefield. We analyzed 2 million crashes to find out why."

Formula B: "[Surprising number] [surprising fact about topic]."
Example: "610,000 injured. 2,923 killed. Here's when NYC's roads are deadliest."

Formula C: "The [superlative] [thing] is [counterintuitive answer]."
Example: "The most dangerous hour isn't 2 AM. It's 5 PM."

Requirements:
- Use specific numbers from the data
- Make it dramatic and specific
- 12-25 words
- Present tense for impact

Return ONLY the headline, nothing else."""
    
    print("Generating headline with Claude...")
    headline = ask_claude(headline_prompt)
    if headline:
        # Clean up headline
        headline = headline.strip().strip('"').strip("'")
        article["headline"] = headline
        print(f"✅ Headline: {headline}\n")
    
    print("="*70)
    print("📝 GENERATING LEDE")
    print("="*70 + "\n")
    
    # Generate lede paragraph
    lede_prompt = f"""You are writing the opening lede for RecordsReveal investigative journalism.

Headline: {article['headline']}

Key findings:
- Dataset: {stats.get('total_records', 'N/A')} records analyzed
- Peak pattern: {stats.get('peak_hour', 'N/A')}
- Geographic leader: {stats.get('top_location', 'N/A')} with {stats.get('top_location_count', 'N/A')} incidents
- Dominant category: {stats.get('majority_category', 'N/A')} at {stats.get('majority_pct', 'N/A')}
- Top entity: {stats.get('top_entity', 'N/A')} ({stats.get('top_entity_amount', 'N/A')})
- Total financial: {stats.get('total_financial', 'N/A')}
- Comparative advantage: {stats.get('comparative_advantage', 'N/A')} ({stats.get('comparative_leader', 'N/A')})
- Attack ads: {stats.get('pct_attack', 'N/A')} of spending
- Dominant spender: {stats.get('dominant_spender', 'N/A')} ({stats.get('dominant_spender_amount', 'N/A')})
- Top 10 concentration: {stats.get('top_10_pct', 'N/A')}
- Top state: {stats.get('top_state', 'N/A')} ({stats.get('top_state_amount', 'N/A')})
- Micro-targeting: {stats.get('micro_target_entity', 'N/A')} ({stats.get('micro_target_transactions', 'N/A')} transactions)

Write a lede using the INVESTIGATION_PLAYBOOK formula:
[Setup conventional assumption] → [Reveal data contradicts it] → [State finding]

EXAMPLE OF GOOD RECORDSREVEAL LEDE:
"If you live in New York City and drive home at 5:00 PM on a weekday, you are statistically entering the most dangerous hour of your entire week. Not 2:00 AM when the drunk drivers are out. Not rush hour in the morning. 5:00 PM."

Requirements:
- 3-5 sentences
- Start with a relatable human scenario
- Contradict conventional wisdom if possible
- Use specific numbers and times
- Make it personal and immediate
- Write in present tense

Return ONLY the lede paragraph, nothing else."""
    
    print("Generating lede...")
    lede = ask_claude(lede_prompt)
    if lede:
        article["lede"] = lede.strip()
        print(f"✅ Lede: {lede[:100]}...\n")
    
    print("="*70)
    print("🔍 GENERATING FINDINGS SECTIONS")
    print("="*70 + "\n")
    
    # Generate findings based on available analyses
    findings = []
    
    # Finding 1: Temporal pattern (if available and has data)
    if 'temporal' in combined.get('analyses', []) and stats.get('peak_hour') and stats.get('peak_hour') != 'N/A':
        print("Writing Finding 1: Temporal Pattern...")
        finding_prompt = f"""Write a findings section for RecordsReveal about temporal patterns.

Data:
- Peak hour: {stats.get('peak_hour', 'N/A')} ({stats.get('peak_hour_count', 'N/A')} records)
- Trend: {stats.get('trend_pct_change', 'N/A')} {stats.get('trend_direction', '')}

EXAMPLE OF GOOD RECORDSREVEAL FINDING:
"This is the finding that should change how you plan your commute. 5:00 PM sees more injuries than any other hour — the evening rush hour when everyone is trying to get home at once, patience is thin, and traffic density peaks.

But the deadliest hour? That's 4:00 AM. Far fewer crashes happen at 4 AM, but when they do, people die. Speed, alcohol, empty roads, and fatigue combine to make early morning the most lethal time on NYC streets."

Requirements:
- Start with impact statement ("This is the finding that...")
- Use specific numbers and times from the data
- Explain human behavior/implications
- 2-3 paragraphs
- Conversational, direct tone
- Present tense
- Bold the key numbers (use **number**)

Return ONLY the text, no title."""
        
        finding = ask_claude(finding_prompt)
        if finding:
            findings.append({
                "title": "Peak Activity Pattern",
                "body": finding.strip(),
                "stat": f"{stats.get('peak_hour_count', 'N/A')} at peak"
            })
            print(f"✅ Finding 1 complete\n")
    
    # Finding 2: Geographic pattern (if available and has data)
    if 'geographic' in combined.get('analyses', []) and stats.get('top_location') and stats.get('top_location') != 'N/A':
        print("Writing Finding 2: Geographic Pattern...")
        finding_prompt = f"""Write a findings section for RecordsReveal about geographic patterns.

Data:
- Top location: {stats.get('top_location', 'N/A')}
- Count: {stats.get('top_location_count', 'N/A')} incidents

EXAMPLE OF GOOD RECORDSREVEAL FINDING:
"Brooklyn leads in total crash injuries with 142,978 people hurt over 11 years. But Manhattan's roads are deadlier — 312 people killed, the highest fatality count of any borough.

Why? Manhattan's grid layout, higher traffic speeds on avenues, and the sheer density of pedestrians all contribute. Brooklyn has more crashes because it has more cars. Manhattan has more deaths because its crashes are more severe."

Requirements:
- State the geographic leader with specific number
- Compare to second place if available
- Explain WHY this location leads (demographics, infrastructure, density)
- 2-3 paragraphs
- Bold key numbers
- Present tense

Return ONLY the text, no title."""
        
        finding = ask_claude(finding_prompt)
        if finding:
            findings.append({
                "title": "Geographic Concentration",
                "body": finding.strip(),
                "stat": stats.get('top_location_count', 'N/A')
            })
            print(f"✅ Finding 2 complete\n")
    
    # Finding 3: Category distribution (if available and has data)
    if 'categorical' in combined.get('analyses', []) and stats.get('majority_category') and stats.get('majority_category') != 'N/A':
        print("Writing Finding 3: Category Pattern...")
        finding_prompt = f"""Write a findings section for RecordsReveal about category distribution.

Data:
- Dominant category: {stats.get('majority_category', 'N/A')}
- Percentage: {stats.get('majority_pct', 'N/A')}

EXAMPLE OF GOOD RECORDSREVEAL FINDING:
"The single most cited known cause of NYC crashes? Driver inattention/distraction at 19.9%. Phones, passengers, navigation screens — anything that takes your eyes off the road for even two seconds.

But here's the problem: 34.3% of all crashes are listed as 'Unspecified.' That's 692,913 crashes with no identified cause. Either the reporting is incomplete, or NYPD officers aren't investigating thoroughly enough to assign a factor."

Requirements:
- State the dominant category with specific percentage
- Explain what this means in human terms
- Identify any problems or surprises in the distribution
- 2-3 paragraphs
- Bold key percentages
- Present tense

Return ONLY the text, no title."""
        
        finding = ask_claude(finding_prompt)
        if finding:
            findings.append({
                "title": "Dominant Category",
                "body": finding.strip(),
                "stat": stats.get('majority_pct', 'N/A')
            })
            print(f"✅ Finding 3 complete\n")
    
    # Finding 4: Financial pattern (if available)
    if 'comparative_financial' in combined.get('analyses', []):
        print("Writing Finding 4: Financial Pattern...")
        finding_prompt = f"""Write a findings section for RecordsReveal about financial patterns.

Data (8 dimensions analyzed):
- Top entity: {stats.get('top_entity', 'N/A')} ({stats.get('top_entity_amount', 'N/A')})
- Total financial: {stats.get('total_financial', 'N/A')}
- Comparative advantage: {stats.get('comparative_advantage', 'N/A')} ({stats.get('comparative_leader', 'N/A')})
- Attack ads: {stats.get('pct_attack', 'N/A')} of all spending
- Dominant spender: {stats.get('dominant_spender', 'N/A')} spent {stats.get('dominant_spender_amount', 'N/A')} across {stats.get('dominant_spender_districts', 0)} districts
- Concentration: Top 10 districts = {stats.get('top_10_pct', 'N/A')} of all spending
- Top state: {stats.get('top_state', 'N/A')} with {stats.get('top_state_amount', 'N/A')} across {stats.get('top_state_districts', 0)} districts
- Micro-targeting: {stats.get('micro_target_entity', 'N/A')} had {stats.get('micro_target_transactions', 'N/A')} transactions (surgical spending)

EXAMPLE OF GOOD RECORDSREVEAL FINANCIAL FINDING:
"The money tells the real story. Democrats hold a **$76 million** financial advantage across swing districts—outspending Republicans by 73%. That's not just a fundraising edge. That's an air war, ground game, and digital dominance all rolled into one number.

The top district for total spending? Colorado's 8th, where **$24.6 million** poured in from both sides. That's $101 per voter. In a district that flipped by just 2,500 votes in 2022, every dollar mattered—and one side had a lot more dollars."

Requirements:
- Start with "The money tells the real story" or similar financial framing
- Use specific dollar amounts from the data
- Explain what this spending means in human terms (per voter, per household, etc.)
- Include competitive context (margins, swing districts, etc.)
- 2-3 paragraphs
- Bold key dollar amounts (use **$amount**)
- Present tense

Return ONLY the text, no title."""
        
        finding = ask_claude(finding_prompt)
        if finding:
            findings.append({
                "title": "Financial Advantage",
                "body": finding.strip(),
                "stat": stats.get('comparative_advantage', 'N/A')
            })
            print(f"✅ Finding 4 complete\n")
    
    article["findings"] = findings
    
    print("="*70)
    print("💬 EXTRACTING PULL QUOTES")
    print("="*70 + "\n")
    
    # Extract pull quotes from Ollama insights
    pull_quotes = []
    insights = combined.get('all_ollama_insights', {})
    
    for analysis_type, insight_text in insights.items():
        if isinstance(insight_text, str):
            # Look for pull quote markers
            lines = insight_text.split('\n')
            for line in lines:
                if 'pull quote' in line.lower() or 'quote:' in line.lower():
                    # Try to extract quoted text
                    if '"' in line:
                        start = line.find('"')
                        end = line.rfind('"')
                        if start != -1 and end > start:
                            quote = line[start+1:end]
                            if 5 <= len(quote.split()) <= 25:
                                pull_quotes.append(quote)
    
    # If we didn't find quotes, generate some
    if not pull_quotes and findings:
        print("Generating pull quotes from findings...")
        quote_prompt = f"""Create 2 compelling pull quotes for RecordsReveal from these findings:

{findings[0]['body'] if findings else 'Data analysis reveals patterns.'}

EXAMPLE OF GOOD RECORDSREVEAL PULL QUOTE:
"The 5 PM spike proves that crash frequency is driven by traffic volume, not driver behavior. More cars = more crashes. It's simple physics."

Requirements:
- 10-20 words each
- Include a specific number or statistic
- Make it quotable and memorable
- No quotation marks needed
- Present tense

Return just the 2 quotes, one per line."""
        
        quotes_text = ask_claude(quote_prompt)
        if quotes_text:
            pull_quotes = [q.strip() for q in quotes_text.split('\n') if q.strip()][:2]
    
    article["pull_quotes"] = pull_quotes[:3]
    print(f"✅ Extracted {len(article['pull_quotes'])} pull quotes\n")
    
    print("="*70)
    print("📋 GENERATING METHODOLOGY")
    print("="*70 + "\n")
    
    # Generate methodology section
    methodology_prompt = f"""Write a methodology section for RecordsReveal.

Dataset: {article['dataset']}
Records analyzed: {stats.get('total_records', 'N/A')}
Analyses performed: {', '.join(article['analyses_used'])}

EXAMPLE OF GOOD RECORDSREVEAL METHODOLOGY:
"Dataset: NYC Motor Vehicle Collisions — Crashes (NYC Open Data) · 2,018,963 crashes · 2012-2023 · Downloaded via Kaggle.

Supervised Learning: Linear Regression, Ridge, Lasso, and Random Forest trained on 452,283 crashes with casualties. Target: total_casualties. Best model: Random Forest R²=0.0296 (very low — casualties are unpredictable).

Unsupervised Learning: K-Means clustering (K=4) on crash hour, day, borough, and casualties. PCA explains 52% of variance in 2 dimensions.

Tools: Python · pandas · scikit-learn · Plotly · Kaggle API."

Requirements:
- List dataset source and size
- Mention key analysis methods used
- Keep it brief and technical but accessible
- Use bullet points or clear structure
- 3-5 sentences

Return ONLY the methodology text."""
    
    print("Generating methodology...")
    methodology = ask_claude(methodology_prompt)
    if methodology:
        article["methodology"] = methodology.strip()
        print(f"✅ Methodology: {methodology[:100]}...\n")
    
    # Save article
    output_path = os.path.join(output_dir, "article_content.json")
    with open(output_path, 'w') as f:
        json.dump(article, f, indent=2, default=str)
    
    print("="*70)
    print("✅ ARTICLE WRITING COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Headline: {article['headline']}")
    print(f"Findings: {len(article['findings'])} sections")
    print(f"Pull quotes: {len(article['pull_quotes'])}")
    print(f"Cost: ~$0.01-0.03 (Claude Sonnet 4)\n")
    
    return article

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python write.py <combined_insights.json> <page_data.json> [output_dir]")
        sys.exit(1)
    
    combined_insights_path = sys.argv[1]
    page_data_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "analysis_results"
    
    write_investigation(combined_insights_path, page_data_path, output_dir)
