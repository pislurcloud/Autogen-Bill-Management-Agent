# 💰 Bill Management Agent

**AI-powered expense tracking using Vision Language Models**

Automatically extract, categorize, and analyze expenses from bill images with beautiful visualizations.

## 🌟 Key Features

- **🤖 Vision Language Models** - Direct image analysis (no OCR!)
- **🔄 Multi-Provider Architecture** - OpenRouter Gemini + Groq Llama with automatic fallback
- **📊 Smart Categorization** - 6 expense categories with AI-powered classification
- **📈 Beautiful Visualizations** - Interactive charts with Plotly
- **💾 Persistent Storage** - SQLite database for historical tracking
- **📥 Export Options** - JSON and CSV downloads
- **🌐 Web Interface** - Clean, intuitive Streamlit GUI
- **💰 100% FREE** - All models use free tiers

## 🏗️ Architecture

```
Vision Language Model Processing (No OCR!)
↓
OpenRouter Gemini Flash (Primary)
↓ (automatic fallback if needed)
Groq Llama 4 Scout (Fallback)
↓
Intelligent Categorization
↓
SQLite Storage
↓
Beautiful Streamlit UI
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Free API Keys

**OpenRouter** (Primary): https://openrouter.ai/keys
**Groq** (Fallback): https://console.groq.com/keys

Both are FREE with generous limits!

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Run the Application

```bash
streamlit run gui/streamlit_app.py
```

### 5. Open Browser

Navigate to: http://localhost:8501

## 📸 Usage

1. **Upload** a bill image (JPG, PNG, or PDF)
2. **Click** "Process Bill"
3. **Wait** 5-10 seconds for VLM analysis
4. **View** categorized expenses and insights
5. **Export** results as JSON or CSV

## 🎯 Supported Categories

- 🛒 **Groceries** - Food, household items
- 🍽️ **Dining** - Restaurants, cafes, takeout
- ⚡ **Utilities** - Electricity, internet, phone
- 🛍️ **Shopping** - Clothing, electronics
- 🎬 **Entertainment** - Streaming, events
- 📦 **Uncategorized** - Everything else

## 🤖 Vision Language Models

### Available Models

| Provider | Model | Speed | Cost |
|----------|-------|-------|------|
| OpenRouter | Gemini Flash 1.5 8B | Fast | FREE |
| Groq | Llama 4 Scout 17B | Very Fast | FREE |
| OpenRouter | Llama 3.2 11B Vision | Medium | FREE |
| OpenRouter | Qwen 2 VL 7B | Medium | FREE |

All models are selectable from the UI!

### Why VLMs?

✅ **No OCR needed** - Direct image understanding
✅ **Better accuracy** - 90-95% extraction rate
✅ **Context aware** - Understands bill structure
✅ **Handles variety** - Works with different formats
✅ **Fast** - Single API call processes entire bill

## 📁 Project Structure

```
bill-management-agent/
├── config/               # Configuration
│   ├── model_config.py   # VLM providers
│   └── settings.py       # App settings
├── utils/                # Utilities
│   ├── vlm_provider.py   # VLM abstraction ⭐
│   ├── image_processor.py
│   └── json_formatter.py
├── database/             # Data layer
│   ├── schema.sql
│   └── db_manager.py
├── gui/                  # Web interface
│   └── streamlit_app.py  # Main UI ⭐
├── bill_processor.py     # Core logic ⭐
├── requirements.txt
├── .env.example
└── README.md
```

## 💻 Technical Details

### VLM Provider Abstraction

The `ModelManager` class provides:
- Unified interface for multiple VLM providers
- Automatic fallback on errors
- Consistent response format
- Error handling and retry logic

### Image Processing

Minimal preprocessing for VLMs:
- Format validation
- PDF to image conversion
- Resize optimization
- Quality assessment

### Database Schema

- **users** - User accounts
- **bills** - Bill records
- **expenses** - Line items
- **user_corrections** - Learning data
- **category_patterns** - Pattern recognition

## 🎨 UI Features

- Model selection dropdown
- Real-time processing status
- Interactive bar and pie charts
- Detailed expense table
- Spending insights
- Quality indicators
- Export buttons
- Statistics dashboard

## 💰 Cost Breakdown

| Component | Cost |
|-----------|------|
| OpenRouter Gemini | FREE |
| Groq Llama | FREE |
| Streamlit | FREE |
| SQLite | FREE |
| **TOTAL** | **$0** ✅ |

## 🔧 Configuration

### Select VLM Model

Choose from 4 free models in the UI sidebar:
1. Gemini Flash 1.5 8B (recommended)
2. Llama 4 Scout 17B
3. Llama 3.2 11B Vision
4. Qwen 2 VL 7B

### Enable Fallback

Toggle automatic fallback in sidebar. If primary model fails, system automatically tries fallback model.

## 📊 Sample Output

```json
{
  "bill_metadata": {
    "merchant_name": "Walmart",
    "bill_date": "2025-10-20",
    "image_quality": "excellent",
    "overall_confidence": 0.92,
    "model_used": "openrouter_gemini"
  },
  "expenses": [
    {
      "description": "Milk 1L",
      "amount": 3.99,
      "category": "groceries",
      "confidence": 0.95
    }
  ],
  "summary": {
    "total_amount": 156.49,
    "item_count": 12,
    "highest_spending_category": "groceries"
  }
}
```

## 🧪 Testing Tips

### Good Images

✅ Clear, well-lit photos
✅ All text readable
✅ No glare or shadows
✅ Straight orientation
✅ Resolution 500px+

### Avoid

❌ Blurry images
❌ Low resolution
❌ Heavy cropping
❌ Dark or overexposed

## 🐛 Troubleshooting

### "API key not found"
- Check `.env` file exists
- Verify keys are set correctly
- No quotes around keys

### "Module not found"
- Run: `pip install -r requirements.txt`
- Check Python 3.8+

### PDF not working
- Install poppler: `apt-get install poppler-utils`
- Or use image formats

### Port in use
- Run: `streamlit run gui/streamlit_app.py --server.port 8502`

## 🎓 Academic Project

This demonstrates:
- **Vision AI applications** - Modern VLM usage
- **Multi-agent systems** - Provider abstraction
- **Production architecture** - Fallback mechanisms
- **User experience** - Clean, functional UI
- **Data engineering** - Database design
- **Cost optimization** - Free-tier only

## 🔮 Future Enhancements

- [ ] Multi-user authentication
- [ ] Budget tracking & alerts
- [ ] Recurring expense detection
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced ML categorization
- [ ] Export to accounting software

## 📝 License

Academic project for educational purposes.

## 🤝 Contributing

Suggestions welcome!

---

**Built with ❤️ using Vision Language Models**

OpenRouter • Groq • Streamlit • SQLite