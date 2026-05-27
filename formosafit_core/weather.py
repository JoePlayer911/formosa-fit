"""
Weather Module — Fetches current weather for Taiwan cities.
Uses wttr.in (free, no API key required).
"""

import logging
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Major Taiwan cities with their Chinese names
TAIWAN_CITIES = {
    "台北 Taipei": "Taipei",
    "新北 New Taipei": "New+Taipei",
    "桃園 Taoyuan": "Taoyuan",
    "台中 Taichung": "Taichung",
    "台南 Tainan": "Tainan",
    "高雄 Kaohsiung": "Kaohsiung",
    "新竹 Hsinchu": "Hsinchu",
    "基隆 Keelung": "Keelung",
    "嘉義 Chiayi": "Chiayi",
    "花蓮 Hualien": "Hualien",
    "屏東 Pingtung": "Pingtung",
    "宜蘭 Yilan": "Yilan",
}


@dataclass
class WeatherInfo:
    city: str
    temperature_c: int
    feels_like_c: int
    humidity: int
    description: str
    wind_speed_kmh: int
    uv_index: int
    rain_chance: int

    def to_prompt_text(self) -> str:
        """Format weather info for LLM prompt."""
        return (
            f"{self.city}: {self.temperature_c}°C (體感 {self.feels_like_c}°C), "
            f"濕度 {self.humidity}%, {self.description}, "
            f"風速 {self.wind_speed_kmh} km/h, "
            f"UV指數 {self.uv_index}, "
            f"降雨機率 {self.rain_chance}%"
        )

    def to_display_text(self) -> str:
        """Format for UI display."""
        return (
            f"🌡️ {self.temperature_c}°C (feels like {self.feels_like_c}°C) | "
            f"💧 {self.humidity}% humidity | "
            f"☁️ {self.description} | "
            f"🌧️ {self.rain_chance}% rain chance | "
            f"☀️ UV {self.uv_index}"
        )


def get_weather(city: str = "台北 Taipei") -> WeatherInfo:
    """
    Fetch current weather for a Taiwan city using wttr.in.
    
    Args:
        city: city name from TAIWAN_CITIES keys, or any city name
        
    Returns:
        WeatherInfo dataclass with current conditions
    """
    # Map Chinese city name to English for API
    query_city = TAIWAN_CITIES.get(city, city.split()[-1] if " " in city else city)
    
    try:
        url = f"https://wttr.in/{query_city}?format=j1"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "FormosaFit/1.0"})
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("lang_zh", [{}])
        if weather_desc:
            desc = weather_desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "Unknown"))
        else:
            desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")

        # Get rain chance from hourly forecast
        hourly = data.get("weather", [{}])[0].get("hourly", [{}])
        rain_chance = 0
        if hourly:
            rain_chances = [int(h.get("chanceofrain", 0)) for h in hourly[:8]]
            rain_chance = max(rain_chances) if rain_chances else 0

        return WeatherInfo(
            city=city,
            temperature_c=int(current.get("temp_C", 25)),
            feels_like_c=int(current.get("FeelsLikeC", 25)),
            humidity=int(current.get("humidity", 70)),
            description=desc,
            wind_speed_kmh=int(current.get("windspeedKmph", 10)),
            uv_index=int(current.get("uvIndex", 5)),
            rain_chance=rain_chance,
        )

    except Exception as e:
        logger.warning(f"Weather API failed for {city}: {e}. Using defaults.")
        return WeatherInfo(
            city=city,
            temperature_c=28,
            feels_like_c=32,
            humidity=75,
            description="多雲 Partly Cloudy",
            wind_speed_kmh=12,
            uv_index=6,
            rain_chance=30,
        )


def get_city_list() -> list:
    """Return list of available Taiwan cities for UI dropdowns."""
    return list(TAIWAN_CITIES.keys())
