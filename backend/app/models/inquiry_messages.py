import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class InquiryMessages(Base):
    __tablename__ = "inquiry_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    inquiry_id = Column(BigInteger, ForeignKey("inquiries.id"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    inquiry = relationship("Inquiries", back_populates="messages", foreign_keys=[inquiry_id])
    sender = relationship("User", back_populates="inquiry_messages", foreign_keys=[sender_id])
