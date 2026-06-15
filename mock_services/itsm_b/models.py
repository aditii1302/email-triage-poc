from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from mock_services.itsm_b.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(20), unique=True, index=True, nullable=False)
    summary = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    reporter = Column(String(255), nullable=True)
    assignee = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="Open")
    priority = Column(String(50), nullable=True)
    issue_type = Column(String(50), nullable=False, default="Task")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    comments = relationship(
        "IssueComment",
        back_populates="issue",
        cascade="all, delete-orphan",
    )


class IssueComment(Base):
    __tablename__ = "issue_comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    author = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    issue = relationship("Issue", back_populates="comments")
