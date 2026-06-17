from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from backend.app.models.base import Base


class TicketLink(Base):
    __tablename__ = "ticket_links"

    id = Column(Integer, primary_key=True, index=True)
    itsm_a_id = Column(String(255), nullable=False, index=True)
    itsm_a_number = Column(String(100), nullable=False, index=True)
    itsm_b_id = Column(String(255), nullable=True)
    itsm_b_key = Column(String(100), nullable=True, index=True)
    raw_email_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
