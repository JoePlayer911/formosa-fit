"""
FormosaFit AI — Gradio Standalone App (Version 1)
Taiwan-localized smart fashion recommendation system.
"""

import os
import sys
import json
import logging
import gradio as gr
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from formosafit_core.vlm_analyzer import VLMAnalyzer
from formosafit_core.product_db import ProductDB
from formosafit_core.fashion_advisor import FashionAdvisor
from formosafit_core.weather import get_weather, get_city_list, TAIWAN_CITIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global State ---
DATA_PATH = str(Path(__file__).parent / "data" / "seed_data.json")
product_db = ProductDB()
if Path(DATA_PATH).exists():
    product_db.load(DATA_PATH)
    logger.info(f"Loaded {len(product_db.products)} products")

SCENES = [
    "👔 辦公室上班 Office Work",
    "💼 科技業上班 Tech Office",
    "🍷 餐廳約會 Restaurant Date",
    "☕ 咖啡廳約會 Café Date",
    "🛍️ 逛街購物 Shopping",
    "🌳 戶外散步 Outdoor Walk",
    "🏃 運動健身 Exercise",
    "🎉 朋友聚會 Party",
    "✈️ 國內旅遊 Domestic Travel",
    "👔 面試 Job Interview",
    "💒 婚禮 Wedding",
    "🎓 畢業典禮 Graduation",
]

STYLE_PREFS = [
    "簡約 Minimal", "都會 Urban", "日系 Japanese",
    "韓系 Korean", "街頭 Streetwear", "正式 Formal",
    "浪漫 Romantic", "機能 Technical", "文青 Artsy",
]


def analyze_and_recommend(
    image, scene, city, style_prefs, budget,
    vlm_provider, vlm_model, vlm_api_key, vlm_base_url,
    llm_provider, llm_model, llm_api_key, llm_base_url,
):
    """Main pipeline: VLM analysis → Product search → LLM recommendation."""
    if image is None:
        yield "❌ 請先上傳一張全身照 / Please upload a full-body photo first.", "{}"
        return

    # --- Step 1: VLM Analysis ---
    yield "🔍 **Step 1/4** — 分析照片中... Analyzing photo with VLM...", "{}"

    vlm = VLMAnalyzer(
        provider=vlm_provider or "ollama",
        model=vlm_model or "moondream",
        api_key=vlm_api_key or None,
        base_url=vlm_base_url or None,
    )
    features = vlm.analyze(image)
    features_json = json.dumps(features, ensure_ascii=False, indent=2)

    yield f"🔍 **Step 1/4** — VLM 分析完成 ✅\n\n", features_json

    # --- Step 2: Weather ---
    yield f"🌤️ **Step 2/4** — 取得天氣資料... Fetching weather for {city}...", features_json

    weather_info = get_weather(city)
    weather_text = weather_info.to_prompt_text()

    yield f"🌤️ **Step 2/4** — 天氣: {weather_info.to_display_text()} ✅\n\n", features_json

    # --- Step 3: Product Search ---
    yield "🔎 **Step 3/4** — 搜尋商品資料庫... Searching product catalog...", features_json

    # Build search query from VLM features + scene
    body_type = features.get("body_type", "")
    gender = features.get("gender_presentation", "")
    search_query = f"{body_type} {scene} {' '.join(style_prefs) if style_prefs else ''}"
    matched_products = product_db.search(search_query, top_k=15)

    product_summary = f"Found {len(matched_products)} matching products"
    yield f"🔎 **Step 3/4** — 找到 {len(matched_products)} 件匹配商品 ✅\n\n", features_json

    # --- Step 4: LLM Recommendation ---
    yield "✨ **Step 4/4** — 生成穿搭推薦... Generating outfit recommendations...\n\n---\n\n", features_json

    advisor = FashionAdvisor(
        provider=llm_provider or "ollama",
        model=llm_model or "llama3.2:3b",
        api_key=llm_api_key or None,
        base_url=llm_base_url or None,
    )

    prefs_text = ", ".join(style_prefs) if style_prefs else "無特別偏好"
    if budget:
        prefs_text += f" | 預算: {budget}"

    accumulated = "✨ **穿搭推薦報告 Outfit Recommendations**\n\n---\n\n"
    for chunk in advisor.generate_recommendation_stream(
        vlm_features=features,
        products=matched_products,
        scene=scene,
        weather=weather_text,
        preferences=prefs_text,
    ):
        accumulated += chunk
        yield accumulated, features_json

    yield accumulated + "\n\n---\n✅ 分析完成 Analysis Complete!", features_json


# --- Build Gradio UI ---
CUSTOM_CSS = """
.gradio-container { max-width: 1400px !important; }
.main-title {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5em !important;
    font-weight: 800 !important;
    margin-bottom: 0 !important;
}
.subtitle {
    text-align: center;
    color: #888;
    font-size: 1.1em;
    margin-top: 0;
}
#analyze-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-size: 1.2em !important;
    padding: 12px 24px !important;
    border: none !important;
    border-radius: 12px !important;
}
#analyze-btn:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.settings-accordion { border: 1px solid #e0e0e0; border-radius: 8px; }
"""

with gr.Blocks(css=CUSTOM_CSS, title="FormosaFit AI 智慧穿搭推薦", theme=gr.themes.Soft()) as app:

    gr.HTML('<h1 class="main-title">🇹🇼 FormosaFit AI</h1>')
    gr.HTML('<p class="subtitle">智慧穿搭推薦系統 — Smart Fashion Recommendation System</p>')

    with gr.Row():
        # --- Left Column: Inputs ---
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="📸 上傳全身照 Upload Full-Body Photo",
                type="filepath",
                height=350,
            )

            scene_input = gr.Dropdown(
                choices=SCENES,
                value=SCENES[0],
                label="🎯 穿搭場景 Occasion",
            )

            city_input = gr.Dropdown(
                choices=get_city_list(),
                value="台北 Taipei",
                label="🌤️ 城市 City (for weather)",
            )

            style_input = gr.CheckboxGroup(
                choices=STYLE_PREFS,
                label="🎨 風格偏好 Style Preferences",
                value=["簡約 Minimal"],
            )

            budget_input = gr.Radio(
                choices=["低 Budget", "中 Mid-range", "中高 Premium", "高 Luxury"],
                value="中 Mid-range",
                label="💰 預算 Budget",
            )

            analyze_btn = gr.Button(
                "🚀 開始分析 Start Analysis",
                variant="primary",
                elem_id="analyze-btn",
            )

            # Collapsible VLM features display
            with gr.Accordion("📊 VLM 特徵分析 Feature Analysis", open=False):
                features_output = gr.Code(
                    label="VLM Features (JSON)",
                    language="json",
                    interactive=False,
                )

        # --- Right Column: Output ---
        with gr.Column(scale=2):
            recommendation_output = gr.Markdown(
                label="📋 穿搭推薦報告 Outfit Recommendations",
                value="👈 上傳照片並點擊「開始分析」\n\nUpload a photo and click 'Start Analysis' to get personalized outfit recommendations!",
            )

    # --- Settings Accordion ---
    with gr.Accordion("⚙️ 模型設定 Model Settings", open=False, elem_classes="settings-accordion"):
        gr.Markdown("### VLM Settings (Vision / Image Analysis)")
        with gr.Row():
            vlm_provider = gr.Dropdown(
                choices=["ollama", "openai", "gemini"],
                value="ollama",
                label="VLM Provider",
            )
            vlm_model = gr.Textbox(
                value="moondream",
                label="VLM Model Name",
                info="ollama: moondream, llava | openai: gpt-4o | gemini: gemini-pro-vision",
            )
        with gr.Row():
            vlm_api_key = gr.Textbox(
                label="VLM API Key (cloud only)",
                type="password",
                placeholder="sk-... or AIza...",
            )
            vlm_base_url = gr.Textbox(
                label="VLM Base URL (optional override)",
                placeholder="http://localhost:11434",
            )

        gr.Markdown("### LLM Settings (Fashion Reasoning)")
        with gr.Row():
            llm_provider = gr.Dropdown(
                choices=["ollama", "openai", "gemini"],
                value="ollama",
                label="LLM Provider",
            )
            llm_model = gr.Textbox(
                value="llama3.2:3b",
                label="LLM Model Name",
                info="ollama: llama3.2:3b | openai: gpt-4o | gemini: gemini-pro",
            )
        with gr.Row():
            llm_api_key = gr.Textbox(
                label="LLM API Key (cloud only)",
                type="password",
                placeholder="sk-... or AIza...",
            )
            llm_base_url = gr.Textbox(
                label="LLM Base URL (optional override)",
                placeholder="http://localhost:11434",
            )

    # --- Footer ---
    gr.Markdown(
        "<center style='color:#aaa; margin-top:20px;'>"
        "FormosaFit AI v1.0 — Powered by VLM + LLM | "
        "Privacy-first: images are processed in-memory only"
        "</center>"
    )

    # --- Event Handlers ---
    analyze_btn.click(
        fn=analyze_and_recommend,
        inputs=[
            image_input, scene_input, city_input, style_input, budget_input,
            vlm_provider, vlm_model, vlm_api_key, vlm_base_url,
            llm_provider, llm_model, llm_api_key, llm_base_url,
        ],
        outputs=[recommendation_output, features_output],
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
    )
