# AI Writer Setup Guide

## ✅ What's Been Installed

The following packages have been successfully installed:
- `anthropic` (v0.103.1) - Claude API client
- `python-dotenv` (v1.2.1) - Environment variable manager

## 🔑 Add Your API Key

### Step 1: Create .env file

Open your terminal and run:

```bash
cd /Users/robgonzalez/Documents/Claude/Projects/recordsreveal-site
nano .env
```

### Step 2: Add your API key

Paste this line into the file:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Replace `sk-ant-api03-your-actual-key-here` with your real API key from https://console.anthropic.com/settings/keys

### Step 3: Save and exit

- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

### Step 4: Verify it works

```bash
python3 /tmp/test_api_key.py
```

You should see: `✅ API key found and looks valid!`

## 🚀 Using the AI Writer

### Basic Usage

```bash
python3 ai_writer.py \
  analysis_examples/car-crashes-50k/article_content.json \
  analysis_examples/car-crashes-50k/results.json \
  --dataset-name "NYC Car Crashes"
```

### What It Does

1. Reads your analysis results
2. Calls Claude API to write:
   - Compelling headline
   - Narrative subhead
   - 3-paragraph intro/lede
   - 3 detailed finding sections
   - Conclusion paragraph
   - Social media titles
3. Outputs `full_article.json` with all content
4. Shows cost estimate (~$0.30 per article)

### Output Structure

The `full_article.json` contains:

```json
{
  "meta": {...},           // Original analysis metadata
  "hero": {...},           // Statistics for hero banner
  "findings": [...],       // Original feature importance data
  "methodology": {...},    // Original model info
  "ai_content": {
    "headline": "...",
    "subhead": "...",
    "og_title": "...",
    "og_description": "...",
    "lede": "...",
    "intro_paragraph_2": "...",
    "intro_paragraph_3": "...",
    "findings": [
      {
        "number": 1,
        "title": "...",
        "description": "...",
        "pull_quote": "..."
      },
      ...
    ],
    "conclusion": "..."
  },
  "ai_meta": {
    "generated_at": "...",
    "model": "claude-sonnet-4-20250514",
    "version": "1.0"
  }
}
```

## 💰 Cost

Claude API pricing:
- Input tokens: $0.003 per 1K tokens
- Output tokens: $0.015 per 1K tokens

Typical article generation:
- ~1,500 input tokens (~$0.0045)
- ~2,000 output tokens (~$0.03)
- **Total: ~$0.30 per article**

## 🎯 Quality Expectations

The AI writer will generate:

✅ **Journalism-quality prose** that matches RecordsReveal's tone
✅ **Compelling headlines** with narrative hooks
✅ **Contextual findings** with human implications
✅ **Pull quotes** for emphasis
✅ **Social media snippets** optimized for sharing

You should still **review and edit** the output - it gets you 85-90% there, but you may want to:
- Adjust specific wording
- Add domain-specific insights
- Tweak headlines for your preferred angle
- Enhance with additional context

## 🔒 Security

- `.env` file is in `.gitignore` (if not, add it!)
- Never commit your API key to Git
- Keep your API key private
- Monitor usage at https://console.anthropic.com/

## 🐛 Troubleshooting

### "No API key found"
Make sure `.env` file exists and contains:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### "API key format looks wrong"
Your key should start with `sk-ant-api03-` or similar

### "Failed to parse JSON"
The AI occasionally returns malformed JSON. Run the command again - it usually works on retry.

### Import errors
Reinstall packages:
```bash
pip3 install anthropic python-dotenv
```

## 📚 Next Steps

Once the AI writer is working:
1. Test it on your 50K sample
2. Review the output quality
3. Build `build_investigation_html.py` to inject AI content into HTML templates
4. Create complete automation pipeline

---

**Need help?** Check the main README or review the script at `ai_writer.py`
