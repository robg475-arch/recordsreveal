#!/usr/bin/env python3
"""
AI-Powered Article Writer for RecordsReveal
============================================

Transforms analysis results into journalism-quality prose using Claude API.

Takes article_content.json and generates:
- Compelling headlines
- Narrative ledes
- Rich finding descriptions
- Contextual implications
- Pull quotes

Usage:
    python3 ai_writer.py article_content.json results.json --dataset-name "NYC Car Crashes"

Requirements:
    pip install anthropic python-dotenv
    
Environment:
    ANTHROPIC_API_KEY in .env file
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install anthropic python-dotenv")
    sys.exit(1)

# Load API key from .env
load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in .env file")
    print("\nCreate a .env file with:")
    print("ANTHROPIC_API_KEY=sk-ant-...")
    sys.exit(1)

client = Anthropic(api_key=api_key)


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def build_prompt(article_data, results_data, dataset_name):
    """Build comprehensive prompt for Claude"""
    
    meta = article_data.get('meta', {})
    hero = article_data.get('hero', {})
    findings = article_data.get('findings', [])
    methodology = article_data.get('methodology', {})
    
    # Extract key stats
    total_records = hero.get('total_records', 0)
    model_accuracy = round(meta.get('r2_score', 0) * 100, 1)
    best_model = methodology.get('best_model', 'Unknown')
    task_type = methodology.get('task_type', 'analysis')
    
    # Build findings summary
    findings_text = "\n".join([
        f"{i+1}. {f['feature']}: {round(f['importance']*100, 1)}% importance"
        for i, f in enumerate(findings[:3])
    ])
    
    # Story angle context
    angle_context = {
        'We cracked the code': 'High accuracy model - we found a clear formula/pattern',
        'The chaos theory': 'Low accuracy - randomness dominates',
        'The pattern hunter': 'Moderate accuracy - patterns exist but are complex'
    }.get(meta.get('angle', ''), 'Data reveals interesting patterns')
    
    prompt = f"""You are writing a data journalism article for RecordsReveal, a newspaper that uses machine learning to investigate public datasets.

DATASET: {dataset_name}
RECORDS ANALYZED: {total_records:,}
MODEL ACCURACY: {model_accuracy}% (R² score)
BEST MODEL: {best_model}
TASK TYPE: {task_type}
STORY ANGLE: {angle_context}

TOP 3 FINDINGS (by feature importance):
{findings_text}

YOUR TASK:
Write compelling, journalism-quality content that matches RecordsReveal's tone and style.

TONE GUIDELINES:
- Direct, punchy, investigative journalism
- Start with the most compelling fact
- Use concrete examples and human implications
- Avoid academic jargon - write for general public
- Be bold with claims backed by data
- Use present tense for impact ("reveals", "shows", "proves")
- Include skepticism/challenge conventional wisdom when relevant

STRUCTURE YOUR RESPONSE AS JSON:
{{
  "headline": "Main headline (12-20 words, punchy, reveals the key finding)",
  "subhead": "Subheadline (20-35 words, adds context and intrigue)",
  "og_title": "Social media title (under 60 chars, clickworthy)",
  "og_description": "Social media description (under 150 chars)",
  "lede": "Opening paragraph (3-5 sentences, hook the reader with the most compelling finding and its human implications)",
  "intro_paragraph_2": "Second paragraph (2-4 sentences, explain what you did and why it matters)",
  "intro_paragraph_3": "Third paragraph (1-2 sentences, transition to findings)",
  "findings": [
    {{
      "number": 1,
      "title": "Finding headline (8-15 words, state the insight clearly)",
      "description": "2-3 paragraphs explaining what this finding means, why it matters, and its implications. Include specific percentages from the data. Make it conversational and compelling.",
      "pull_quote": "A memorable one-sentence quote summarizing this finding (suitable for sidebar highlighting)"
    }},
    ... (repeat for each of the top 3 findings)
  ],
  "conclusion": "Final paragraph tying it all together (2-3 sentences, what does this mean going forward?)"
}}

EXAMPLES OF GOOD RECORDSREVEAL WRITING:

HEADLINE EXAMPLE:
"Every weekday at 5:00 PM, New York City's roads become a battlefield. We analyzed 2 million crashes to find out why."

LEDE EXAMPLE:
"If you live in New York City and drive home at 5:00 PM on a weekday, you are statistically entering the most dangerous hour of your entire week. Not 2:00 AM when the drunk drivers are out. Not rush hour in the morning. 5:00 PM."

FINDING EXAMPLE:
"This is the finding that should change how you plan your commute. 5:00 PM sees more injuries than any other hour — the evening rush hour when everyone is trying to get home at once, patience is thin, and traffic density peaks."

Now write the article content for {dataset_name}. Return ONLY valid JSON, no other text."""

    return prompt


def generate_article(article_data, results_data, dataset_name):
    """Call Claude API to generate article content"""
    
    print(f"\n🤖 Generating article content using Claude API...")
    print(f"   Dataset: {dataset_name}")
    print(f"   Records: {article_data['hero']['total_records']:,}")
    
    prompt = build_prompt(article_data, results_data, dataset_name)
    
    model_used = None
    
    try:
        # Try multiple models in order of preference
        models_to_try = [
            "claude-sonnet-4-5-20250929",  # Sonnet 4.5 (latest - same as OpenCode)
            "claude-3-5-sonnet-20241022",  # Sonnet 3.5 (fallback)
        ]
        
        last_error = None
        model_used = None
        for model in models_to_try:
            try:
                message = client.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=1,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                model_used = model
                print(f"✅ Using model: {model}")
                break
            except Exception as e:
                last_error = e
                continue
        else:
            # All models failed
            raise last_error
        
        response_text = message.content[0].text
        
        # Remove markdown code blocks if present
        if response_text.strip().startswith('```'):
            # Extract content between ```json and ```
            lines = response_text.strip().split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]  # Remove opening ```json
            if lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove closing ```
            response_text = '\n'.join(lines)
        
        # Parse JSON response
        article_json = json.loads(response_text)
        
        print("✅ Article generated successfully!")
        
        # Show preview
        print(f"\n📰 Preview:")
        print(f"   Headline: {article_json['headline'][:80]}...")
        print(f"   Findings: {len(article_json['findings'])} sections generated")
        
        # Calculate cost based on model
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        
        # Pricing per model (per 1M tokens)
        if "sonnet-4" in model_used:
            # Sonnet 4.5 pricing
            cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        else:
            # Sonnet 3.5 pricing
            cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        
        print(f"\n💰 Cost: ${cost:.4f} ({input_tokens} in, {output_tokens} out)")
        
        return article_json, model_used
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Claude's response as JSON")
        print(f"   Error: {e}")
        print(f"\n   Raw response:")
        print(response_text[:500])
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)


def merge_with_original(article_data, ai_content, model_used):
    """Merge AI-generated content with original article_content.json"""
    
    # Keep original structure but add AI content
    enhanced = article_data.copy()
    
    # Add AI content
    enhanced['ai_content'] = {
        'headline': ai_content['headline'],
        'subhead': ai_content['subhead'],
        'og_title': ai_content['og_title'],
        'og_description': ai_content['og_description'],
        'lede': ai_content['lede'],
        'intro_paragraph_2': ai_content['intro_paragraph_2'],
        'intro_paragraph_3': ai_content['intro_paragraph_3'],
        'findings': ai_content['findings'],
        'conclusion': ai_content['conclusion']
    }
    
    # Add metadata
    enhanced['ai_meta'] = {
        'generated_at': datetime.now().isoformat(),
        'model': model_used or 'claude-sonnet-4-20250514',
        'version': '1.0'
    }
    
    return enhanced


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 ai_writer.py <article_content.json> <results.json> [--dataset-name 'Name']")
        print("\nExample:")
        print("  python3 ai_writer.py analysis_results/article_content.json analysis_results/results.json --dataset-name 'NYC Car Crashes'")
        sys.exit(1)
    
    article_path = Path(sys.argv[1])
    results_path = Path(sys.argv[2])
    
    # Parse dataset name
    dataset_name = "Data Investigation"
    if '--dataset-name' in sys.argv:
        idx = sys.argv.index('--dataset-name')
        if idx + 1 < len(sys.argv):
            dataset_name = sys.argv[idx + 1]
    
    # Validate files
    if not article_path.exists():
        print(f"❌ Article file not found: {article_path}")
        sys.exit(1)
    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("RecordsReveal AI Article Writer")
    print("=" * 60)
    
    # Load data
    print(f"\n📂 Loading files...")
    article_data = load_json(article_path)
    results_data = load_json(results_path)
    print(f"   ✅ {article_path}")
    print(f"   ✅ {results_path}")
    
    # Generate article
    ai_content, model_used = generate_article(article_data, results_data, dataset_name)
    
    # Merge with original
    enhanced_article = merge_with_original(article_data, ai_content, model_used)
    
    # Save output
    output_path = article_path.parent / "full_article.json"
    with open(output_path, 'w') as f:
        json.dump(enhanced_article, f, indent=2)
    
    print(f"\n✅ Complete article saved to:")
    print(f"   {output_path}")
    
    print(f"\n📊 Output structure:")
    print(f"   - Original data: meta, hero, findings, methodology")
    print(f"   - AI content: headline, subhead, lede, {len(ai_content['findings'])} findings, conclusion")
    print(f"   - Ready for HTML generation")
    
    print("\n" + "=" * 60)
    print("✅ AI WRITING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
