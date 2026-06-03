"""
Fashion Advisor — LLM-powered outfit recommendation engine.
Constructs prompts from VLM features + products + context, calls LLM for reasoning.
Supports both local (Ollama/Kuwa) and cloud (OpenAI/Gemini) LLMs.
"""

import json
import logging
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are FormosaFit AI (FormosaFit AI 穿搭助理), a professional fashion consultant specializing in Taiwan-localized styling.

Your expertise includes:
- Understanding Taiwan's climate (humid subtropical, afternoon thunderstorms, 30°C+ summers)
- Local fashion contexts (辦公室上班, 中山區約會, 夜市逛街, 機車通勤)
- Body type analysis and flattering silhouette recommendations
- Color theory adapted to Asian skin tones
- Practical comfort-meets-style solutions

RULES:
1. Always recommend exactly 3 complete outfit options
2. Each outfit must include: top, bottom, shoes, and at least 1 accessory
3. Explain WHY each item flatters the user's body type
4. Consider Taiwan's weather and the specific occasion
5. Suggest color coordination with reasoning
6. Be bilingual — use Traditional Chinese (繁體中文) for item names and English for explanations
7. Format output in clean Markdown with clear sections
8. CRITICAL: Respect the user's gender_presentation from the VLM analysis. If masculine/male, recommend ONLY menswear. If feminine/female, recommend ONLY womenswear. NEVER cross-recommend."""

RECOMMENDATION_PROMPT_TEMPLATE = """Based on the following analysis, recommend 3 complete outfit options.

## 👤 Body & Style Analysis (VLM Features)
{vlm_features}

## 🎯 Occasion / Scene
{scene}

## 🌤️ Weather Conditions
{weather}

## 👗 Available Products from Catalog
{products}

## 🎨 User Preferences
{preferences}

---

Please provide 3 outfit recommendations in the following format for EACH outfit:

### 🔷 方案 [N]: [Outfit Theme Name]

**Complete Look:**
| 單品 Item | 推薦 Recommendation | 顏色 Color |
|-----------|---------------------|------------|
| 上衣 Top | ... | ... |
| 下裝 Bottom | ... | ... |
| 鞋子 Shoes | ... | ... |
| 配件 Accessories | ... | ... |

**🎨 Color Coordination / 色彩搭配理由:**
[Explain why these colors work together]

**👔 Fit & Body Type / 版型與體型修飾:**
[Explain how each item flatters this body type]

**🌡️ Climate Suitability / 氣候適應:**
[Why this works for Taiwan's weather + the specific occasion]

**💡 Styling Tips / 穿搭小技巧:**
[Extra tips for pulling this look together]
"""


class FashionAdvisor:
    """Generates outfit recommendations using LLM reasoning."""

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama3.2:3b",
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
        else:
            self.base_url = "http://localhost:11434"

    def generate_recommendation(
        self,
        vlm_features: dict,
        products: list,
        scene: str = "日常休閒 casual",
        weather: str = "台北 30°C 濕度75% 晴天",
        preferences: str = "無特別偏好",
    ) -> str:
        """
        Generate outfit recommendations (non-streaming).
        Returns the full recommendation text.
        """
        prompt = self._build_prompt(vlm_features, products, scene, weather, preferences)
        
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        else:
            return self._call_openai_compatible(prompt)

    def generate_recommendation_stream(
        self,
        vlm_features: dict,
        products: list,
        scene: str = "日常休閒 casual",
        weather: str = "台北 30°C 濕度75% 晴天",
        preferences: str = "無特別偏好",
    ):
        """
        Generate outfit recommendations (streaming).
        Yields chunks of text as they arrive.
        """
        prompt = self._build_prompt(vlm_features, products, scene, weather, preferences)
        
        if self.provider == "ollama":
            yield from self._call_ollama_stream(prompt)
        else:
            yield from self._call_openai_stream(prompt)

    def _build_prompt(
        self, vlm_features: dict, products: list, scene: str, weather: str, preferences: str
    ) -> str:
        """Construct the full recommendation prompt."""
        # Format VLM features
        if isinstance(vlm_features, dict):
            features_text = json.dumps(vlm_features, ensure_ascii=False, indent=2)
        else:
            features_text = str(vlm_features)

        # Format products list
        if products:
            products_text = "\n".join(
                f"- {p.to_display_text() if hasattr(p, 'to_display_text') else str(p)}"
                for p in products
            )
        else:
            products_text = "No specific products available. Please recommend general items suitable for Taiwan."

        return RECOMMENDATION_PROMPT_TEMPLATE.format(
            vlm_features=features_text,
            scene=scene,
            weather=weather,
            products=products_text,
            preferences=preferences,
        )

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API (non-streaming)."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 4096},
        }
        resp = requests.post(url, json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json().get("response", "")

    def _call_ollama_stream(self, prompt: str):
        """Call Ollama API (streaming)."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": True,
            "options": {"temperature": 0.7, "num_predict": 4096},
        }
        resp = requests.post(url, json=payload, timeout=180, stream=True)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                text = chunk.get("response", "")
                if text:
                    yield text

    def _call_openai_compatible(self, prompt: str) -> str:
        """Call OpenAI-compatible API (non-streaming)."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, json=payload, headers=headers, timeout=180)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_openai_stream(self, prompt: str):
        """Call OpenAI-compatible API (streaming)."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True,
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, json=payload, headers=headers, timeout=180, stream=True)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0].get("delta", {})
                    text = delta.get("content", "")
                    if text:
                        yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
