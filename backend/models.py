# backend/models.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from datetime import datetime
from db import Base

class Issuer(Base):
    __tablename__ = "issuers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    asset_class: Mapped[str] = mapped_column(String(64), index=True)
    scores = relationship("CreditScore", back_populates="issuer", cascade="all, delete-orphan")

class CreditScore(Base):
    __tablename__ = "credit_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issuer_id: Mapped[int] = mapped_column(ForeignKey("issuers.id"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    score: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(32))
    issuer = relationship("Issuer", back_populates="scores")
    attributions = relationship("FeatureAttribution", back_populates="score_row", cascade="all, delete-orphan")

class FeatureAttribution(Base):
    __tablename__ = "feature_attributions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score_id: Mapped[int] = mapped_column(ForeignKey("credit_scores.id"))
    feature_name: Mapped[str] = mapped_column(String(128))
    feature_value: Mapped[float] = mapped_column(Float)
    shap_value: Mapped[float] = mapped_column(Float)
    score_row = relationship("CreditScore", back_populates="attributions")

class NewsEvent(Base):
    __tablename__ = "news_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issuer_id: Mapped[int] = mapped_column(ForeignKey("issuers.id"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(128))
    payload: Mapped[dict] = mapped_column(JSON)
