# Generate Hero Image Skill

Automatically generates professional hero images for investigations using Leonardo.ai API.

## What It Does

1. **Detects investigation type** from combined insights (police, traffic, aviation, hollywood)
2. **Selects appropriate prompt** based on type
3. **Calls Leonardo.ai API** to generate image
4. **Polls for completion** (waits 30-60 seconds)
5. **Downloads image** to `images/heroes/{investigation_id}.jpg`

## Requirements

- Leonardo.ai API key (free tier: 150 daily tokens)
- Python packages: `requests`, `python-dotenv`

## Setup

1. **Add API key to `.env`:**
   ```
   LEONARDO_API_KEY=your-key-here
   ```

2. **Install dependencies:**
   ```bash
   pip3 install requests python-dotenv
   ```

## Usage

### Manual
```bash
python3 generate.py <combined_insights.json> <investigation_id>
```

### In Pipeline
Automatically called between STEP 5 (Write) and STEP 6 (Build HTML)

## Prompts

The skill uses different prompts based on investigation type:

- **Police/Force**: City map with data points at night
- **Traffic/Crashes**: Manhattan skyline with heat map overlay
- **Aviation/Bird Strikes**: Airplane with flight path data lines
- **Hollywood/Movies**: Film reel with bar chart elements
- **Default**: Abstract data journalism visualization

## Output

- **File**: `images/heroes/{investigation_id}.jpg`
- **Size**: ~100-150 KB
- **Dimensions**: 1024x768px
- **Format**: JPEG

## Cost

- Free tier: 150 tokens/day (~30 images)
- Each generation uses ~5 tokens
- Cost: $0.00 on free tier

## Error Handling

If generation fails:
- Pipeline continues without hero image
- You can generate manually at leonardo.ai
- Logs show error details

## Integration

Fully integrated into `run_full_pipeline.sh` as Step 5.5.

No manual intervention needed - just run the pipeline!
