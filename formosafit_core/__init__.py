"""
FormosaFit AI Core Library
Taiwan-localized smart fashion recommendation system powered by VLM + LLM.
"""

from .vlm_analyzer import VLMAnalyzer
from .product_db import ProductDB
from .fashion_advisor import FashionAdvisor
from .weather import get_weather

__version__ = "1.0.0"
__all__ = ["VLMAnalyzer", "ProductDB", "FashionAdvisor", "get_weather"]
