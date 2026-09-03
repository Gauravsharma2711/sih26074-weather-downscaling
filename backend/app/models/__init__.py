"""Database models package."""
from backend.app.models.panchayat_weather import PanchayatWeatherData
from backend.app.models.downscaled_forecast import DownscaledForecast

__all__ = ["PanchayatWeatherData", "DownscaledForecast"]
