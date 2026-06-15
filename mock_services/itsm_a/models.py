from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from mock_services.itsm_a.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    sys_id = Column(String(36), unique=True, index=True, nullable=False)
    number = Column(String(20), unique=True, index=True, nullable=False)
    short_description = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    caller_id = Column(String(255), nullable=True)
    state = Column(String(50), nullable=False, default="new")
    urgency = Column(String(20), nullable=True)
    impact = Column(String(20), nullable=True)
    assignment_group = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
