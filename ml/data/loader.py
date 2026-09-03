import logging
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.panchayat_weather import PanchayatWeatherData

logger = logging.getLogger(__name__)


def load_panchayat_weather_data(
    db: Optional[Session] = None,
    limit: Optional[int] = None
) -> pd.DataFrame:
    """
    Load raw Panchayat weather observations and block forecasts from the database.
    
    Args:
        db: Optional SQLAlchemy session. If not provided, a temporary session is created.
        limit: Optional maximum number of rows to retrieve.
        
    Returns:
        pd.DataFrame containing the raw panchayat weather records.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
        
    try:
        query = db.query(PanchayatWeatherData)
        if limit is not None:
            query = query.limit(limit)
            
        statement = query.statement
        df = pd.read_sql(statement, db.bind)
        logger.info(f"Loaded {len(df)} records from panchayat_weather_data.")
        return df
    finally:
        if close_session:
            db.close()
