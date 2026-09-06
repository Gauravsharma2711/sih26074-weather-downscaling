"""Database models package."""
from backend.app.models.panchayat_weather import PanchayatWeatherData
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.models.block_forecast import BlockForecast
from backend.app.models.advisory import Advisory

__all__ = ["PanchayatWeatherData", "DownscaledForecast", "BlockForecast", "Advisory"]
