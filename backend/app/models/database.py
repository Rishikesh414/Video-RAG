"""
SQLAlchemy ORM models for the VideoRAG database.
Defines the PostgreSQL table schemas for users, uploads, and chat history.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
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
    uploads = relationship("Upload", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Upload(Base):
    """Upload model — tracks uploaded videos and PDFs."""

    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(Enum("video", "pdf", name="file_type", native_enum=False), nullable=False)
    file_path = Column(String(1000), nullable=False)
    status = Column(String(50), default="processing")  # processing | completed | failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploads")


class ChatMessage(Base):
    """ChatMessage model — stores user queries and AI responses."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    video_timestamp = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
