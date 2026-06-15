from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from mock_services.directory.database import Base


class DirectoryUser(Base):
    __tablename__ = "directory_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    upn = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    manager = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
