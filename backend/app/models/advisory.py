from sqlalchemy import Column, BigInteger, Text, Numeric, Date, DateTime, func
from backend.app.core.database import Base


class Advisory(Base):
    """
    SQLAlchemy Model for the 'advisories' table in Supabase PostgreSQL.
    Stores deterministic agricultural advisories linked to downscaled panchayat forecasts.
    """
    __tablename__ = "advisories"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, nullable=False)
    panchayat_id = Column(BigInteger, index=True, nullable=False)
    forecast_id = Column(BigInteger, nullable=True)
    forecast_date = Column(Date, nullable=False, index=True)
    rainfall_mm = Column(Numeric, nullable=True)
    rainfall_category = Column(Text, nullable=True)
    severity = Column(Text, nullable=True)
    advisory_title = Column(Text, nullable=True)
    advisory_text = Column(Text, nullable=True)
    rule_version = Column(Text, nullable=True)
    status = Column(Text, default="DRAFT", index=True, nullable=True)
    officer_id = Column(Text, nullable=True)
    officer_comment = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Advisory(id={self.id}, panchayat_id={self.panchayat_id}, "
            f"forecast_date={self.forecast_date}, severity={self.severity}, "
            f"status={self.status})>"
        )
