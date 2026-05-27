"""
FormosaFit AI — Kuwa OS Executor (Version 2)
Integrates into Kuwa Multi-Chat UI as a custom LLMExecutor.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(Path(__file__).parent))

from kuwa.executor import LLMExecutor, Modelfile
from kuwa.executor.llm_executor import extract_user_attachment
from kuwa.executor.multi_modality import (
    get_supported_image_mime,
    fetch_image,
    image_to_data_url,
)

from formosafit_core.vlm_analyzer import VLMAnalyzer, image_to_base64
from formosafit_core.product_db import ProductDB
from formosafit_core.fashion_advisor import FashionAdvisor, SYSTEM_PROMPT
from formosafit_core.weather import get_weather, TAIWAN_CITIES

logger = logging.getLogger(__name__)


class FormosaFitExecutor(LLMExecutor):
    """Kuwa executor that runs the full FormosaFit pipeline."""

    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        vlm_group = parser.add_argument_group("VLM Options")
        vlm_group.add_argument(
            "--vlm_provider", default="ollama",
            choices=["ollama", "openai", "gemini"],
            help="VLM provider for image analysis",
        )
        vlm_group.add_argument(
            "--vlm_model", default="moondream",
            help="VLM model name (e.g., moondream, gpt-4o)",
        )
        vlm_group.add_argument(
            "--vlm_api_key", default=None,
            help="API key for cloud VLM",
        )
        vlm_group.add_argument(
            "--vlm_base_url", default=None,
            help="Custom base URL for VLM API",
        )

        llm_group = parser.add_argument_group("LLM Options")
        llm_group.add_argument(
            "--llm_provider", default="ollama",
            choices=["ollama", "openai", "gemini"],
            help="LLM provider for fashion reasoning",
        )
        llm_group.add_argument(
            "--llm_model", default="llama3.2:3b",
            help="LLM model name",
        )
        llm_group.add_argument(
            "--llm_api_key", default=None,
            help="API key for cloud LLM",
        )
        llm_group.add_argument(
            "--llm_base_url", default=None,
            help="Custom base URL for LLM API",
        )

        data_group = parser.add_argument_group("Data Options")
        data_group.add_argument(
            "--product_db_path",
            default=str(Path(__file__).parent / "data" / "seed_data.json"),
            help="Path to product catalog JSON",
        )

    def setup(self):
        self.stop = False

        # Initialize VLM
        self.vlm = VLMAnalyzer(
            provider=self.args.vlm_provider,
            model=self.args.vlm_model,
            api_key=self.args.vlm_api_key,
            base_url=self.args.vlm_base_url,
        )

        # Initialize Product DB
        self.product_db = ProductDB()
        db_path = self.args.product_db_path
        if Path(db_path).exists():
            self.product_db.load(db_path)
            logger.info(f"Loaded {len(self.product_db.products)} products")

        # Initialize LLM advisor
        self.advisor = FashionAdvisor(
            provider=self.args.llm_provider,
            model=self.args.llm_model,
            api_key=self.args.llm_api_key,
            base_url=self.args.llm_base_url,
        )

        logger.info("FormosaFit executor initialized successfully")

    def _extract_scene_and_preferences(self, text: str) -> dict:
        """Parse user message for scene, city, and preferences."""
        text_lower = text.lower()
        result = {
            "scene": "日常休閒 casual",
            "city": "台北 Taipei",
            "preferences": "",
            "clean_text": text,
        }

        # Detect scene keywords
        scene_map = {
            "上班": "👔 辦公室上班 Office Work",
            "辦公": "👔 辦公室上班 Office Work",
            "office": "👔 辦公室上班 Office Work",
            "約會": "🍷 約會 Date",
            "date": "🍷 約會 Date",
            "逛街": "🛍️ 逛街購物 Shopping",
            "shopping": "🛍️ 逛街購物 Shopping",
            "運動": "🏃 運動健身 Exercise",
            "面試": "👔 面試 Job Interview",
            "interview": "👔 面試 Job Interview",
            "婚禮": "💒 婚禮 Wedding",
            "wedding": "💒 婚禮 Wedding",
            "休閒": "🌳 休閒 Casual",
            "casual": "🌳 休閒 Casual",
            "旅遊": "✈️ 旅遊 Travel",
            "travel": "✈️ 旅遊 Travel",
        }
        for keyword, scene in scene_map.items():
            if keyword in text_lower:
                result["scene"] = scene
                break

        # Detect city
        for city_name in TAIWAN_CITIES.keys():
            if any(part in text for part in city_name.split()):
                result["city"] = city_name
                break

        result["preferences"] = text
        return result

    async def llm_compute(self, history: list[dict], modelfile: Modelfile):
        try:
            self.stop = False

            # Extract images from chat history
            history_with_attachments = extract_user_attachment(
                history, allowed_mime_type=get_supported_image_mime()
            )

            # Find the latest image
            image_url = None
            for msg in reversed(history_with_attachments):
                if msg.get("attachments"):
                    image_url = msg["attachments"][0]["url"]
                    break

            # Get user's text message
            user_text = ""
            for msg in reversed(history):
                if msg["role"] == "user":
                    user_text = msg["content"]
                    break

            if not image_url:
                yield (
                    "📸 **請上傳一張全身照！**\n\n"
                    "Please upload a full-body photo to get started.\n\n"
                    "💡 **使用方式 / How to use:**\n"
                    "1. 上傳全身照 Upload a full-body photo\n"
                    "2. 告訴我你的穿搭場景 Tell me your occasion\n"
                    "   例如 Example: `上班`, `約會`, `逛街`, `面試`\n"
                    "3. 可選：指定城市 Optionally specify a city\n"
                    "   例如 Example: `台北`, `高雄`, `台中`\n\n"
                    "我會分析你的照片，推薦 3 套適合的穿搭方案！\n"
                    "I'll analyze your photo and recommend 3 outfit options!"
                )
                return

            # Parse scene and preferences from text
            context = self._extract_scene_and_preferences(user_text)

            # --- Step 1: VLM Analysis ---
            yield "🔍 **Step 1/4** — 分析照片中... Analyzing your photo...\n\n"
            if self.stop:
                return

            # Fetch the image and analyze
            try:
                pil_image = fetch_image(image_url)
                features = self.vlm.analyze(pil_image)
            except Exception as e:
                logger.exception("VLM analysis failed")
                features = {
                    "error": str(e),
                    "body_type": "standard",
                    "current_clothing": [],
                    "styling_notes": "Could not analyze image",
                }

            features_text = json.dumps(features, ensure_ascii=False, indent=2)
            yield f"✅ VLM 分析完成\n\n<details><summary>📊 VLM Features</summary>\n\n```json\n{features_text}\n```\n</details>\n\n"
            if self.stop:
                return

            # --- Step 2: Weather ---
            yield "🌤️ **Step 2/4** — 取得天氣資料...\n\n"
            weather = get_weather(context["city"])
            yield f"🌤️ {weather.to_display_text()}\n\n"
            if self.stop:
                return

            # --- Step 3: Product Search ---
            yield "🔎 **Step 3/4** — 搜尋商品...\n\n"
            body_type = features.get("body_type", "")
            search_query = f"{body_type} {context['scene']} {context['preferences']}"
            products = self.product_db.search(search_query, top_k=15)
            yield f"📦 找到 {len(products)} 件匹配商品\n\n---\n\n"
            if self.stop:
                return

            # --- Step 4: LLM Recommendation ---
            yield "✨ **Step 4/4** — 生成穿搭推薦...\n\n"

            for chunk in self.advisor.generate_recommendation_stream(
                vlm_features=features,
                products=products,
                scene=context["scene"],
                weather=weather.to_prompt_text(),
                preferences=context["preferences"] or "無特別偏好",
            ):
                if self.stop:
                    return
                yield chunk

            yield "\n\n---\n✅ 分析完成 Analysis Complete!"

        except Exception as e:
            logger.exception("FormosaFit error")
            yield f"❌ Error: {str(e)}"

    async def abort(self):
        self.stop = True
        logger.debug("aborted")
        return "Aborted"


if __name__ == "__main__":
    executor = FormosaFitExecutor()
    executor.run()
