# 🇹🇼 FormosaFit AI — 智慧穿搭推薦系統

**Taiwan-localized Smart Fashion Recommendation System powered by VLM + LLM**

Upload a full-body photo → AI analyzes your body type & current outfit → Recommends 3 complete outfits tailored to Taiwan's climate, your occasion, and personal style.

## Features

- 📸 **VLM Photo Analysis** — Extracts body type, clothing features, colors, and proportions
- 🔍 **Smart Product Search** — Vector DB semantic search over clothing catalog
- 🌤️ **Taiwan Weather** — Real-time weather integration for climate-appropriate suggestions
- 👔 **3 Outfit Recommendations** — Complete looks with color coordination and body-type reasoning
- 🌐 **Bilingual** — Traditional Chinese + English output

## Two Versions

### Version 1: Gradio Standalone (`app_gradio.py`)
Self-contained web app. No Kuwa dependency required.

```bash
# Quick start
cd c:\kuwa\formosafit
pip install -r requirements_gradio.txt
python app_gradio.py
# Opens at http://localhost:7860
```

Or use the Windows launcher: `run_gradio.bat`

### Version 2: Kuwa OS Executor (`formosafit_executor.py`)
Integrates into Kuwa Multi-Chat UI as a native executor.

```bash
# Start the executor (with Kuwa OS running)
python formosafit_executor.py --access_code .tool/formosafit --product_db_path data/seed_data.json
```

Or use the Windows launcher: `kuwa_executor\run.bat`

**Bot files** (import via Kuwa Store):
- `formosafit.bot` — Custom executor version (full features)
- `formosafit_vlm.bot` — Agent pipeline version (no-code, simpler)

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
├── app_gradio.py              # Version 1: Gradio standalone
├── formosafit_executor.py     # Version 2: Kuwa executor
├── formosafit.bot             # Kuwa bot config
├── formosafit_vlm.bot         # Kuwa agent pipeline bot
├── requirements_gradio.txt
├── run_gradio.bat
└── kuwa_executor/
    └── run.bat
```

## Pipeline

```
Photo → VLM (moondream/gpt-4o) → Feature JSON
                                       ↓
                              Product DB Search (ChromaDB)
                                       ↓
Weather API (wttr.in) ──→ LLM (llama3.2/gpt-4o) → 3 Outfit Reports
```
