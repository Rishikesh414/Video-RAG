"""
SQLAlchemy ORM models for the VideoRAG database.
Defines dynamic table schemas for users, uploads, and chat history.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class User(Base):
    """User model — stores student and faculty accounts."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum("student", "faculty", name="user_role", native_enum=False), nullable=False, default="student")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class Upload(Base):
    """Upload model — tracks uploaded videos and PDFs."""

    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(Enum("video", "pdf", name="file_type", native_enum=False), nullable=False)
    file_path = Column(String(1000), nullable=False)
    module = Column(String(50), nullable=False, default="M1", index=True)
    file_size = Column(BigInteger, default=0)
    status = Column(String(50), default="processing", index=True)  # processing | completed | failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploads")


class ChatMessage(Base):
    """ChatMessage model — stores user queries and AI responses."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    video_timestamp = Column(Float, nullable=True)
    confidence = Column(String(50), nullable=True, default="high")  # high | medium | low
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
