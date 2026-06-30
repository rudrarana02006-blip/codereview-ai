from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    raw_input = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    overall_rating = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    risks = relationship("Risk", back_populates="review", cascade="all, delete-orphan")
    suggestions = relationship("Suggestion", back_populates="review", cascade="all, delete-orphan")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)

    review = relationship("Review", back_populates="risks")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    description = Column(Text, nullable=False)
    line_reference = Column(String(100), nullable=True)

    review = relationship("Review", back_populates="suggestions")

# Pydantic schemas for API
from pydantic import BaseModel
from typing import List, Optional

class RiskSchema(BaseModel):
    description: str
    severity: str

class SuggestionSchema(BaseModel):
    description: str
    line_reference: Optional[str] = None

class ReviewCreate(BaseModel):
    raw_input: str

class ReviewResponse(BaseModel):
    id: int
    raw_input: str
    summary: str
    overall_rating: str
    created_at: datetime
    risks: List[RiskSchema]
    suggestions: List[SuggestionSchema]

    class Config:
        from_attributes = True
