from sqlalchemy import Column, DateTime, String, Integer, BigInteger, ForeignKey,Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.sql import func

from src.utils.db import Base


class DocumentsModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False, index=True  )
    filename = Column(String(255), nullable=False)
    # Where the file is physically stored
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    status = Column(String(50), default="uploaded", nullable=False)
    error_message = Column(Text, nullable=True)
    extracted_text = Column(MEDIUMTEXT, nullable=True)
    generated_notes = Column(MEDIUMTEXT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column( DateTime(timezone=True), server_default=func.now(), onupdate=func.now())