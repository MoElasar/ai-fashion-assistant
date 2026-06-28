"""
Weather Service
Fetches weather data from Open-Meteo API with caching.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from cachetools import TTLCache

# Cache weather data: 30 min for current, 2 hours for forecast
current_weather_cache = TTLCache(maxsize=100, ttl=1800)  # 30 minutes
forecast_cache = TTLCache(maxsize=100, ttl=7200)  # 2 hours


class WeatherService:
    """
    Fetches weather data from Open-Meteo API.
    Free, no API key required.
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def _get_cache_key(self, lat: float, lon: float) -> str:
        """Generate cache key from coordinates."""
        return f"{lat:.2f},{lon:.2f}"
    
    def _map_weather_code(self, code: int) -> str:
        """Map Open-Meteo weather code to description."""
        weather_codes = {
            0: "clear",
            1: "mainly_clear",
            2: "partly_cloudy",
            3: "overcast",
            45: "foggy",
            48: "foggy",
            51: "light_rain",
            53: "moderate_rain",
            55: "heavy_rain",
            61: "light_rain",
            63: "moderate_rain",
            65: "heavy_rain",
            71: "light_snow",
            73: "moderate_snow",
            75: "heavy_snow",
            80: "rain_showers",
            81: "rain_showers",
            82: "heavy_rain_showers",
            95: "thunderstorm",
            96: "thunderstorm",
            99: "thunderstorm"
        }
        return weather_codes.get(code, "unknown")
    
    def _get_clothing_suggestion(self, temp: float, condition: str) -> Dict[str, Any]:
        """Get clothing suggestions based on weather."""
        suggestions = {
            "needs_outerwear": temp < 20,
            "needs_warm_outerwear": temp < 10,
            "needs_rain_protection": condition in ["light_rain", "moderate_rain", "heavy_rain", "rain_showers", "heavy_rain_showers"],
            "light_clothing": temp > 25,
            "warm_clothing": temp < 15
        }
        
        # Layer recommendations
        if temp < 5:
            suggestions["recommended_layers"] = ["top", "outerwear", "bottom", "socks", "footwear"]
            suggestions["outerwear_type"] = "heavy coat"
        elif temp < 15:
            suggestions["recommended_layers"] = ["top", "outerwear", "bottom", "socks", "footwear"]
            suggestions["outerwear_type"] = "jacket"
        elif temp < 20:
            suggestions["recommended_layers"] = ["top", "outerwear", "bottom", "socks", "footwear"]
            suggestions["outerwear_type"] = "light jacket"
        else:
            suggestions["recommended_layers"] = ["top", "bottom", "socks", "footwear"]
            suggestions["outerwear_type"] = None
        
        return suggestions
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get current weather for coordinates.
        Results are cached for 30 minutes.
        """
        cache_key = self._get_cache_key(latitude, longitude)
        
        # Check cache
        if cache_key in current_weather_cache:
            return current_weather_cache[cache_key]
        
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            current = data.get("current", {})
            condition = self._map_weather_code(current.get("weather_code", 0))
            temp = current.get("temperature_2m", 20)
            
            result = {
                "temperature": temp,
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "condition": condition,
                "suggestions": self._get_clothing_suggestion(temp, condition),
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            # Cache result
            current_weather_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for up to 7 days.
        Results are cached for 2 hours.
        """
        cache_key = f"{self._get_cache_key(latitude, longitude)}_forecast"
        
        # Check cache
        if cache_key in forecast_cache:
            return forecast_cache[cache_key]
        
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": days
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            
            forecast = []
            for i, date in enumerate(dates):
                temp_max = daily.get("temperature_2m_max", [20])[i]
                temp_min = daily.get("temperature_2m_min", [15])[i]
                avg_temp = (temp_max + temp_min) / 2
                condition = self._map_weather_code(daily.get("weather_code", [0])[i])
                
                forecast.append({
                    "date": date,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "temp_avg": round(avg_temp, 1),
                    "condition": condition,
                    "precipitation_probability": daily.get("precipitation_probability_max", [0])[i],
                    "suggestions": self._get_clothing_suggestion(avg_temp, condition)
                })
            
            result = {
                "forecast": forecast,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            # Cache result
            forecast_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None


# Global instance
weather_service = WeatherService()