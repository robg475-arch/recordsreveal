#!/usr/bin/env python3
"""
RecordsReveal Generate Hero Image Skill
Uses Leonardo.ai API to generate professional hero images for investigations
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LEONARDO_API_KEY = os.getenv('LEONARDO_API_KEY')
if not LEONARDO_API_KEY:
    print("❌ Error: LEONARDO_API_KEY not found in .env file")
    sys.exit(1)

# Leonardo API endpoints
LEONARDO_API_BASE = "https://cloud.leonardo.ai/api/rest/v1"
GENERATE_ENDPOINT = f"{LEONARDO_API_BASE}/generations"

# Investigation type to prompt mapping
PROMPTS = {
    "police": "Minimalist data journalism illustration, abstract city map at night with glowing red and orange data points, dark charcoal background, cream colored streets, modern editorial style, clean geometric design, professional investigative journalism aesthetic",
    
    "traffic": "Stylized Manhattan skyline silhouette in cream with red and orange heat map overlay showing crash hotspots, dark background, modern data journalism aesthetic, geometric and clean, editorial illustration style",
    
    "aviation": "Editorial illustration of airplane silhouette with geometric bird flight paths as data lines, red and orange paths crossing frame, dark background, cream airplane, modern infographic style, clean and professional",
    
    "hollywood": "Art deco film reel with rising bar chart, minimalist editorial illustration, cream and gold tones with red accents, dark charcoal background, sophisticated data journalism aesthetic",
    
    "default": "Sophisticated editorial illustration representing data journalism and investigative reporting. Abstract geometric shapes, data points, connecting lines, and chart elements in cream, red, and orange on dark charcoal background. Minimalist modern style, professional and clean."
}

def detect_investigation_type(combined_insights_path):
    """Detect investigation type from combined insights"""
    try:
        with open(combined_insights_path, 'r') as f:
            data = json.load(f)
        
        # Check for keywords in insights
        text = json.dumps(data).lower()
        
        if 'police' in text or 'force' in text or 'officer' in text:
            return 'police'
        elif 'traffic' in text or 'crash' in text or 'vehicle' in text or 'nyc' in text:
            return 'traffic'
        elif 'bird' in text or 'aviation' in text or 'aircraft' in text or 'flight' in text:
            return 'aviation'
        elif 'movie' in text or 'film' in text or 'box office' in text or 'hollywood' in text:
            return 'hollywood'
        else:
            return 'default'
    except Exception as e:
        print(f"⚠️  Warning: Could not detect investigation type: {e}")
        return 'default'

def generate_image(prompt, investigation_id):
    """Generate image using Leonardo.ai API"""
    
    print(f"\n🎨 Generating hero image with Leonardo.ai...")
    print(f"   Prompt: {prompt[:80]}...")
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEONARDO_API_KEY}"
    }
    
    payload = {
        "prompt": prompt,
        "num_images": 1,
        "width": 1024,
        "height": 768,
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Phoenix (best for illustrations)
        "photoReal": False,
        "presetStyle": "ILLUSTRATION"
    }
    
    try:
        # Submit generation request
        print("   📤 Sending generation request...")
        response = requests.post(GENERATE_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        generation_id = result['sdGenerationJob']['generationId']
        
        print(f"   ✅ Generation started (ID: {generation_id})")
        print(f"   ⏳ Waiting for image to be ready...")
        
        # Poll for completion
        max_attempts = 60  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(5)  # Wait 5 seconds between checks
            attempt += 1
            
            # Check generation status
            status_url = f"{GENERATE_ENDPOINT}/{generation_id}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            
            if 'generations_by_pk' in status_data:
                gen_status = status_data['generations_by_pk']['status']
                
                if gen_status == 'COMPLETE':
                    # Get image URL
                    images = status_data['generations_by_pk']['generated_images']
                    if images and len(images) > 0:
                        image_url = images[0]['url']
                        print(f"   ✅ Image ready! Downloading...")
                        return download_image(image_url, investigation_id)
                    else:
                        print("   ❌ No images in completed generation")
                        return None
                        
                elif gen_status == 'FAILED':
                    print(f"   ❌ Generation failed")
                    return None
                    
                else:
                    print(f"   ⏳ Still generating... (attempt {attempt}/{max_attempts})")
        
        print("   ⏱️  Timeout waiting for image generation")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None

def download_image(url, investigation_id):
    """Download generated image"""
    try:
        # Create images/heroes directory if it doesn't exist
        output_dir = Path("images/heroes")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Download image
        response = requests.get(url)
        response.raise_for_status()
        
        # Save as JPG
        output_path = output_dir / f"{investigation_id}.jpg"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"   💾 Saved: {output_path} ({file_size:.1f} KB)")
        
        return str(output_path)
        
    except Exception as e:
        print(f"   ❌ Download error: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate.py <combined_insights.json> <investigation_id>")
        sys.exit(1)
    
    insights_path = sys.argv[1]
    investigation_id = sys.argv[2]
    
    print("=" * 70)
    print("🎨 RECORDSREVEAL GENERATE HERO IMAGE")
    print("=" * 70)
    print(f"Investigation ID: {investigation_id}")
    print(f"Insights: {insights_path}")
    print("=" * 70)
    
    # Detect investigation type
    inv_type = detect_investigation_type(insights_path)
    print(f"\n🔍 Detected investigation type: {inv_type.upper()}")
    
    # Get appropriate prompt
    prompt = PROMPTS.get(inv_type, PROMPTS['default'])
    
    # Generate image
    image_path = generate_image(prompt, investigation_id)
    
    if image_path:
        print("\n" + "=" * 70)
        print("✅ HERO IMAGE GENERATION COMPLETE")
        print("=" * 70)
        print(f"Image: {image_path}")
        print(f"Ready to use in HTML build step")
        print()
    else:
        print("\n" + "=" * 70)
        print("❌ HERO IMAGE GENERATION FAILED")
        print("=" * 70)
        print("Continuing pipeline without hero image")
        print("You can generate manually at leonardo.ai")
        print()

if __name__ == "__main__":
    main()
