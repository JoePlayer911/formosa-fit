# 🇹🇼 FormosaFit AI — 智慧穿搭推薦系統

**Taiwan-localized Smart Fashion Recommendation System powered by VLM + LLM**

Upload a full-body photo → AI analyzes your body type & current outfit → Recommends 3 complete outfits tailored to Taiwan's climate, your occasion, and personal style.

## Features

- 📸 **VLM Photo Analysis** — Extracts body type, clothing features, colors, and proportions
- 🔍 **Smart Product Search** — Vector DB semantic search over clothing catalog
- 🌤️ **Taiwan Weather** — Real-time weather integration for climate-appropriate suggestions
- 👔 **3 Outfit Recommendations** — Complete looks with color coordination and body-type reasoning
- 🌐 **Bilingual** — Traditional Chinese + English output

## Quick Start (Gradio Standalone)

The application runs as a self-contained web app.

```bash
# Clone the repository and navigate to the folder
cd formosafit

# Install dependencies
pip install -r requirements_gradio.txt

# Start the application
python app_gradio.py
# Opens at http://localhost:7860
```

Or use the Windows launcher: `run_gradio.bat`

## Model Requirements

### VLM (Image Analysis)
| Model | Provider | VRAM | Quality |
|-------|----------|------|---------|
| **moondream** | Ollama (local) | ~2GB | ⭐⭐⭐ |
| llava | Ollama (local) | ~4GB | ⭐⭐⭐⭐ |
| gpt-4o | OpenAI (cloud) | — | ⭐⭐⭐⭐⭐ |

### LLM (Fashion Reasoning)
| Model | Provider | VRAM | Quality |
|-------|----------|------|---------|
| **llama3.2:3b** | Ollama (local) | ~2GB | ⭐⭐⭐ |
| llama3.1:8b | Ollama (local) | ~5GB | ⭐⭐⭐⭐ |
| gpt-4o | OpenAI (cloud) | — | ⭐⭐⭐⭐⭐ |

### Quick Setup (Local, Free)
```bash
# Install Ollama (https://ollama.com)
ollama pull moondream    # VLM, ~1.7GB
ollama pull llama3.2:3b  # LLM, ~2GB
```

## Project Structure

```
formosafit/
├── formosafit_core/           # Shared core library
│   ├── __init__.py
│   ├── vlm_analyzer.py       # VLM image analysis
│   ├── product_db.py         # Vector DB product search
│   ├── fashion_advisor.py    # LLM recommendation engine
│   └── weather.py            # Taiwan weather (wttr.in)
├── data/
│   └── seed_data.json        # Demo product catalog (35 items)
├── app_gradio.py              # Gradio standalone app
├── requirements_gradio.txt
└── run_gradio.bat
```

## Pipeline

```
Photo → VLM (moondream/gpt-4o) → Feature JSON
                                       ↓
                              Product DB Search (ChromaDB)
                                       ↓
Weather API (wttr.in) ──→ LLM (llama3.2/gpt-4o) → 3 Outfit Reports
```
