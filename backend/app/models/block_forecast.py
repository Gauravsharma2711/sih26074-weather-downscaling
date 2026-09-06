from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Numeric,
    Date,
    DateTime,
    UniqueConstraint,
    Index,
    func
)
from backend.app.core.database import Base


class BlockForecast(Base):
    """
    SQLAlchemy Model for the 'block_forecasts' table in Supabase PostgreSQL.
    Stores raw regional numerical weather prediction rainfall forecasts at Block level.
    """
    __tablename__ = "block_forecasts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, nullable=False)
    district_name = Column(Text, nullable=False, index=True)
    block_name = Column(Text, nullable=False, index=True)
    forecast_issue_date = Column(Date, nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    rainfall_mm = Column(Numeric, nullable=False)
    source = Column(Text, nullable=True)
    source_model = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "district_name",
            "block_name",
            "forecast_issue_date",
            "forecast_date",
            "source_model",
            name="uq_block_forecasts"
        ),
        Index("idx_block_forecasts_district_block", "district_name", "block_name"),
        Index("idx_block_forecasts_forecast_date", "forecast_date"),
        Index("idx_block_forecasts_forecast_issue_date", "forecast_issue_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<BlockForecast(id={self.id}, block='{self.block_name}', "
            f"forecast_date={self.forecast_date}, "
            f"rainfall_mm={self.rainfall_mm}, source_model='{self.source_model}')>"
        )
