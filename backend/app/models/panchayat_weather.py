from sqlalchemy import Column, BigInteger, String, Text, Numeric, Date, DateTime, func
from backend.app.core.database import Base


class PanchayatWeatherData(Base):
    """
    SQLAlchemy Model for the 'panchayat_weather_data' table in Supabase PostgreSQL.
    Stores historical and current Panchayat-level weather observations,
    IMD block forecasts, geographical coordinates, elevation, and ground truth data.
    """
    __tablename__ = "panchayat_weather_data"

    panchayat_id = Column(BigInteger, primary_key=True, index=True, nullable=False)
    lgd_code = Column(BigInteger, nullable=False, index=True)
    panchayat_name = Column(Text, nullable=True)
    block_name = Column(Text, nullable=True, index=True)
    district_name = Column(Text, nullable=True, index=True)
    
    panchayat_latitude = Column(Numeric, nullable=True)
    panchayat_longitude = Column(Numeric, nullable=True)
    elevation_m = Column(Numeric, nullable=True)
    
    date = Column(Date, nullable=True, index=True)
    forecast_issue_date = Column(Date, nullable=True)
    block_forecast_rainfall_mm = Column(Numeric, nullable=True)
    
    station_id = Column(Text, nullable=True)
    station_latitude = Column(Numeric, nullable=True)
    station_longitude = Column(Numeric, nullable=True)
    station_distance_km = Column(Numeric, nullable=True)
    actual_rainfall_mm = Column(Numeric, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PanchayatWeatherData(panchayat_id={self.panchayat_id}, "
            f"name='{self.panchayat_name}', date={self.date}, "
            f"forecast_rainfall={self.block_forecast_rainfall_mm}, "
            f"actual_rainfall={self.actual_rainfall_mm})>"
        )
