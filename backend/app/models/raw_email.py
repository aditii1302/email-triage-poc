from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func

from backend.app.models.base import Base


class RawEmail(Base):
    __tablename__ = "raw_emails"

    id = Column(Integer, primary_key=True, index=True)
    mailbox = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=True, index=True)
    conversation_id = Column(String(255), nullable=True, index=True)
    sender = Column(String(512), nullable=True)
    recipients = Column(JSON, nullable=False, default=list)
    cc = Column(JSON, nullable=False, default=list)
    subject = Column(String(998), nullable=True, index=True)
    body = Column(Text, nullable=True)
    attachment_count = Column(Integer, nullable=False, default=0)
    attachment_paths = Column(JSON, nullable=False, default=list)
    file_path = Column(String(1024), nullable=False)
    status = Column(String(50), nullable=False, default="new")
    received_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
