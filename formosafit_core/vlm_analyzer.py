"""
VLM Analyzer — Extracts body and clothing features from photos.
Supports: Ollama (moondream2/llava), OpenAI Vision, Gemini.
"""

import io
import json
import base64
import logging
import requests
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

# Structured prompt for VLM feature extraction (bilingual)
VLM_ANALYSIS_PROMPT = """You are a professional fashion styling analyst. Analyze this full-body photo and extract the following features. Respond ONLY with valid JSON, no extra text.

你是一位專業時尚造型分析師。請分析這張照片，提取以下特徵。僅以有效 JSON 格式回覆。

{
  "body_type": "body shape category (e.g., slim/標準/athletic/petite/plus-size)",
  "proportions": {
    "upper_lower_ratio": "description of upper vs lower body proportion",
    "shoulder_width": "narrow/standard/broad",
    "waist_position": "high/standard/low"
  },
  "current_clothing": [
    {
      "item": "item name (e.g., T-shirt/polo/jeans)",
      "category": "top/bottom/shoes/outerwear/accessory",
      "color": "color name",
      "fit": "tight/slim/standard/loose/oversized",
      "style": "casual/formal/sporty/streetwear"
    }
  ],
  "skin_tone": "warm/cool/neutral",
  "styling_notes": "areas to flatter or balance (e.g., broaden shoulders, elongate legs)",
  "overall_style": "current overall style impression",
  "gender_presentation": "masculine/feminine/neutral"
}"""


def image_to_base64(image_source) -> str:
    """Convert various image sources to base64 string."""
    if isinstance(image_source, str):
        if image_source.startswith("data:"):
            # Already a data URL, extract base64 part
            return image_source.split(",", 1)[1]
        elif image_source.startswith("http"):
            resp = requests.get(image_source, timeout=30)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("utf-8")
        else:
            # File path
            with open(image_source, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    elif isinstance(image_source, bytes):
        return base64.b64encode(image_source).decode("utf-8")
    elif isinstance(image_source, Image.Image):
        buf = io.BytesIO()
        image_source.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    else:
        raise ValueError(f"Unsupported image source type: {type(image_source)}")


def image_to_data_url(image_source) -> str:
    """Convert image source to a data URL."""
    b64 = image_to_base64(image_source)
    return f"data:image/png;base64,{b64}"


class VLMAnalyzer:
    """Analyzes photos using Vision Language Models."""

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "moondream",
        api_key: str = None,
        base_url: str = None,
    ):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key

        if base_url:
            self.base_url = base_url
        elif self.provider == "ollama":
            self.base_url = "http://localhost:11434"
        elif self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
        elif self.provider == "gemini":
            self.base_url = "https://generativelanguage.googleapis.com"
        else:
            self.base_url = "http://localhost:11434"

    def analyze(self, image_source, custom_prompt: str = None) -> dict:
        """
        Analyze a photo and return structured features.
        
        Args:
            image_source: file path, URL, base64 string, bytes, or PIL Image
            custom_prompt: optional override for the analysis prompt
            
        Returns:
            dict with extracted features
        """
        prompt = custom_prompt or VLM_ANALYSIS_PROMPT
        
        try:
            if self.provider == "ollama":
                raw = self._call_ollama(image_source, prompt)
            elif self.provider in ("openai", "cloud"):
                raw = self._call_openai_compatible(image_source, prompt)
            elif self.provider == "gemini":
                raw = self._call_openai_compatible(image_source, prompt)
            else:
                raw = self._call_ollama(image_source, prompt)

            return self._parse_response(raw)
        except Exception as e:
            logger.exception("VLM analysis failed")
            return {
                "error": str(e),
                "body_type": "unknown",
                "current_clothing": [],
                "styling_notes": "Analysis failed. Please try again.",
            }

    def _call_ollama(self, image_source, prompt: str) -> str:
        """Call Ollama API with image."""
        b64 = image_to_base64(image_source)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [b64],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 2048},
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "")

    def _call_openai_compatible(self, image_source, prompt: str) -> str:
        """Call OpenAI-compatible Vision API."""
        data_url = image_to_data_url(image_source)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.2,
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _parse_response(self, raw_text: str) -> dict:
        """Parse the VLM response into structured JSON."""
        # Try to extract JSON from the response
        text = raw_text.strip()
        
        # Handle markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # Find JSON object boundaries
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        try:
            result = json.loads(text)
            logger.info(f"VLM analysis successful: {list(result.keys())}")
            return result
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse VLM JSON, using raw text. Response: {raw_text[:200]}")
            return {
                "raw_analysis": raw_text,
                "body_type": "unknown",
                "current_clothing": [],
                "styling_notes": raw_text[:500],
            }
