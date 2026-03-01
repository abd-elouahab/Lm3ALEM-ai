"""Job, MatchingAttempt, Guarantee, Payment models."""
from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import (
    SpecialtyEnum,
    ComplexityEnum,
    JobStatusEnum,
    MatchingResponseEnum,
    GuaranteeStatusEnum,
    PaymentStatusEnum,
)


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    artisan_id = Column(Integer, ForeignKey("artisans.id", ondelete="SET NULL"))
    client_name = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    problem_type = Column(SQLEnum(SpecialtyEnum), nullable=False)
    symptom = Column(Text)
    photo_url = Column(String(500))
    ai_description = Column(Text)
    diagnosis_notes = Column(Text, nullable=True)
    severity = Column(Integer)
    surface_area_m2 = Column(Float)
    complexity = Column(SQLEnum(ComplexityEnum))
    nb_elements_affected = Column(Integer)
    estimated_price = Column(Float)
    estimated_duration_hours = Column(Float)
    final_price = Column(Float)
    status = Column(SQLEnum(JobStatusEnum), default=JobStatusEnum.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    confirmed_start = Column(DateTime(timezone=True))
    confirmed_end = Column(DateTime(timezone=True))
    after_photo_url = Column(String(500))
    client = relationship("Client", backref="jobs")
    artisan = relationship("Artisan", backref="jobs")


class MatchingAttempt(Base):
    __tablename__ = "matching_attempts"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    artisan_id = Column(Integer, ForeignKey("artisans.id", ondelete="CASCADE"), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    response = Column(SQLEnum(MatchingResponseEnum), default=MatchingResponseEnum.pending)
    refusal_count = Column(Integer, default=0)
    job = relationship("Job", backref="matching_attempts")
    artisan = relationship("Artisan", backref="matching_attempts")


class Guarantee(Base):
    __tablename__ = "guarantees"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    opened_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(GuaranteeStatusEnum), default=GuaranteeStatusEnum.open)
    complaint_text = Column(Text)
    complaint_photo_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("Job", backref="guarantee", uselist=False)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    artisan_share = Column(Float, nullable=False)
    savings_share = Column(Float, nullable=False)
    platform_share = Column(Float, nullable=False)
    status = Column(SQLEnum(PaymentStatusEnum), default=PaymentStatusEnum.held)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True))
    job = relationship("Job", backref="payment", uselist=False)
