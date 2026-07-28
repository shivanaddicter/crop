import os
import requests

# ── Crop recommendation data ──────────────────────────────────────────────────
CROP_RECOMMENDATIONS = {
    "Rice": {
        "emoji": "🌾",
        "color": "#3b82f6",
        "glow": "rgba(59,130,246,0.15)",
        "tips": [
            "🌊 Maintain 5–10 cm standing water during vegetative stage",
            "🌡️ Ideal temperature range: 20–35°C for optimal growth",
            "💊 Apply nitrogen fertilizer in split doses (basal + top-dress)",
            "🐛 Watch for brown planthopper & blast disease early",
            "📅 Harvest when 80–85% of grains are golden-yellow",
        ],
        "best_season": "Kharif (June–November)",
        "yield_potential": "4–6 tonnes/hectare",
        "water_req": "1200–2000 mm",
    },
    "Sugarcane": {
        "emoji": "🎋",
        "color": "#f59e0b",
        "glow": "rgba(245,158,11,0.15)",
        "tips": [
            "☀️ Requires 12–16 hours of sunlight for high sugar content",
            "💧 Irrigate every 8–10 days; avoid waterlogging",
            "🌱 Plant setts at 75–90 cm row spacing for best yield",
            "🔪 Trash mulching reduces weed pressure and retains moisture",
            "📅 Harvest at 10–12 months for peak sucrose concentration",
        ],
        "best_season": "October–March planting",
        "yield_potential": "70–100 tonnes/hectare",
        "water_req": "1500–2500 mm",
    },
    "Maize": {
        "emoji": "🌽",
        "color": "#f43f5e",
        "glow": "rgba(244,63,94,0.15)",
        "tips": [
            "🌧️ Critical water need at silking and grain-fill stages",
            "🌡️ Optimal germination between 18–24°C soil temperature",
            "📏 Maintain 60–75 cm row spacing with 20–25 cm plant spacing",
            "🌿 Apply potassium-rich fertilizer to improve stalk strength",
            "📅 Harvest when husk turns brown and kernels are hard",
        ],
        "best_season": "Kharif & Rabi seasons",
        "yield_potential": "5–8 tonnes/hectare",
        "water_req": "500–800 mm",
    },
    "Wheat": {
        "emoji": "🌿",
        "color": "#22c55e",
        "glow": "rgba(34,197,94,0.15)",
        "tips": [
            "❄️ Requires cool temperature (10–20°C) during growth stage",
            "💧 First irrigation at Crown Root Initiation (21 days after sowing)",
            "🌱 Sow at 100–125 kg/ha seed rate for optimal plant density",
            "💊 Apply urea top-dressing at tillering for higher grain weight",
            "📅 Harvest when grain moisture drops to 12–14%",
        ],
        "best_season": "Rabi (November–April)",
        "yield_potential": "3–5 tonnes/hectare",
        "water_req": "450–650 mm",
    },
}

# ── Weather helper ────────────────────────────────────────────────────────────
def get_weather(city, api_key=None):
    """
    Fetch current weather data for a city via OpenWeatherMap.

    Args:
        city (str): City name.
        api_key (str): OpenWeatherMap API key. Falls back to env var OPENWEATHER_API_KEY.

    Returns:
        tuple: (temperature, rainfall_1h, humidity) or raises ValueError on failure.
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "")
    if not key:
        raise ValueError(
            "No OpenWeatherMap API key found. "
            "Set the OPENWEATHER_API_KEY environment variable."
        )

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={key}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Weather API request failed: {exc}") from exc

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    rainfall = data.get("rain", {}).get("1h", 0.0)

    return temp, rainfall, humidity