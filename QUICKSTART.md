# 🚀 Quick Start Guide

## Setup in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys (2 min)

#### OpenRouter (Primary VLM)
1. Visit: https://openrouter.ai/keys
2. Sign up/login
3. Create new API key
4. Copy the key

#### Groq (Fallback VLM)
1. Visit: https://console.groq.com/keys
2. Sign up/login  
3. Create new API key
4. Copy the key

**Both are FREE!**

### Step 3: Configure (1 min)

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your keys:
# OPENROUTER_API_KEY=sk-or-v1-xxxxx
# GROQ_API_KEY=gsk_xxxxx
```

### Step 4: Run (1 min)

```bash
streamlit run gui/streamlit_app.py
```

### Step 5: Use It! 

Open browser: http://localhost:8501

1. Upload bill image
2. Click "Process Bill"
3. View results!

## 🎯 Tips for Best Results

### Good Images ✅

- Clear, well-lit photos
- All text readable
- No glare or shadows
- Straight orientation
- 500px+ resolution

### Avoid ❌

- Blurry images
- Low resolution
- Heavy cropping
- Dark/overexposed

## 🤖 How It Works

1. **Upload** → Image validated and prepared
2. **VLM Analysis** → Gemini Flash extracts data
3. **Fallback** → Llama Scout if Gemini fails
4. **Categorization** → AI assigns categories
5. **Storage** → Saved to SQLite database
6. **Display** → Beautiful charts and insights

## 💡 Key Features

- 🤖 Vision Language Models (no OCR!)
- 🔄 Automatic fallback
- 📊 6 expense categories
- 📈 Interactive visualizations
- 💾 Database storage
- 📥 Export JSON/CSV
- 💰 100% FREE

## ❓ Troubleshooting

**Can't find .env file?**
```bash
# Make sure you're in project root
pwd
# Should show: /path/to/bill-management-agent

# Then create .env
cp .env.example .env
```

**API key errors?**
- Check keys in .env file
- No quotes around keys
- No extra spaces
- Keys should start with "sk-" or "gsk_"

**Module not found?**
```bash
pip install -r requirements.txt
```

**PDF not working?**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Or just use JPG/PNG
```

## 🎉 You're Ready!

Start processing your bills with Vision Language Models!

Questions? Check README.md for detailed docs.

---

Happy expense tracking! 💰