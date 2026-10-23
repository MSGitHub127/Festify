"""Data models: SQLAlchemy ORM tables and Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db import Base


class EventType(StrEnum):
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"


# --- SQLAlchemy ORM Tables ---


class EventRecord(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), index=True, nullable=False)
    event_type = Column(String(32), nullable=False)  # wedding | birthday | community
    title = Column(String(255), nullable=False)
    event_date = Column(String(64), nullable=True)
    location = Column(String(255), nullable=True)
    guest_count = Column(Integer, default=100)
    total_budget = Column(Float, default=10000.0)
    vibe_theme = Column(String(255), default="Classic Elegance")
    encrypted_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    expenses = relationship("ExpenseRecord", back_populates="event", cascade="all, delete-orphan")
    milestones = relationship("MilestoneRecord", back_populates="event", cascade="all, delete-orphan")
    vendors = relationship("VendorRecord", back_populates="event", cascade="all, delete-orphan")


class ExpenseRecord(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(64), nullable=False)
    item_name = Column(String(255), nullable=False)
    allocated_amount = Column(Float, default=0.0)
    actual_amount = Column(Float, default=0.0)
    paid = Column(Boolean, default=False)
    vendor_name = Column(String(255), nullable=True)

    event = relationship("EventRecord", back_populates="expenses")


class MilestoneRecord(Base):
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    timeframe = Column(String(32), nullable=False)  # e.g. 12_months, 6_months, 1_week, day_of
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_time = Column(String(64), nullable=True)
    completed = Column(Boolean, default=False)
    owner = Column(String(64), default="Host")

    event = relationship("EventRecord", back_populates="milestones")


class VendorRecord(Base):
    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(64), nullable=False)  # catering, venue, photo, music, decor
    name = Column(String(255), nullable=False)
    quoted_price = Column(Float, default=0.0)
    status = Column(String(32), default="inquiring")  # inquiring, quoted, booked, completed
    risk_level = Column(String(16), default="low")  # low, medium, high
    vetting_score = Column(Float, default=85.0)
    notes = Column(Text, nullable=True)

    event = relationship("EventRecord", back_populates="vendors")


# --- Pydantic Request & Response Schemas ---


class EventCreateRequest(BaseModel):
    event_type: EventType = Field(..., description="Type of event: wedding, birthday, or community")
    title: str = Field(..., min_length=2, max_length=255, description="Event name/title")
    guest_count: int = Field(default=100, ge=1, le=50000, description="Estimated number of guests")
    total_budget: float = Field(default=10000.0, ge=100.0, description="Total budget in USD")
    vibe_theme: str = Field(default="Modern Celebration", description="Desired theme, tone, or aesthetic")
    event_date: str | None = Field(default=None, description="Target event date (YYYY-MM-DD or descriptive)")
    location: str | None = Field(default="Local Venue", description="City, state, or venue type")
    special_requirements: str | None = Field(default=None, description="Dietary, cultural, or special notes")


class CategoryBudget(BaseModel):
    category: str
    percentage: float
    allocated_amount: float
    per_guest_amount: float
    recommended_items: list[str]


class BudgetBreakdown(BaseModel):
    total_budget: float
    guest_count: int
    cost_per_guest: float
    contingency_buffer: float
    categories: list[CategoryBudget]
    cost_saving_tips: list[str]


class TimelineMilestone(BaseModel):
    timeframe: str
    title: str
    description: str
    due_or_time: str
    owner: str


class RunOfShowItem(BaseModel):
    time: str
    activity: str
    location: str
    responsible: str
    notes: str


class TimelinePlan(BaseModel):
    macro_milestones: list[TimelineMilestone]
    day_of_run_of_show: list[RunOfShowItem]
    conflict_warnings: list[str]


class VendorChecklistItem(BaseModel):
    category: str
    must_ask_questions: list[str]
    contract_red_flags: list[str]
    deliverable_milestones: list[str]
    benchmark_percentage: float


class ThemeConcept(BaseModel):
    name: str
    tagline: str
    description: str
    color_palette: list[str]
    decor_accents: list[str]


class MenuItem(BaseModel):
    course: str
    item_name: str
    dietary_tags: list[str]  # e.g. ["Vegan", "Gluten-Free", "Halal"]
    pairing: str


class SpeechDraft(BaseModel):
    speaker_role: str
    tone: str
    draft_text: str


class CreativeIdeas(BaseModel):
    themes: list[ThemeConcept]
    curated_menu: list[MenuItem]
    entertainment_activities: list[str]
    bespoke_favors: list[str]
    speech_toast: SpeechDraft


class StatutoryPermits(BaseModel):
    sound_permit_required: bool
    alcohol_license_notes: str
    food_handling_hygiene: str
    fire_capacity_regulations: str
    weather_backup_plan: str


class FullEventPlanResponse(BaseModel):
    event_id: str
    event_type: str
    title: str
    guest_count: int
    total_budget: float
    vibe_theme: str
    budget: BudgetBreakdown
    timeline: TimelinePlan
    vendor_rubric: list[VendorChecklistItem]
    creative_ideas: CreativeIdeas
    statutory_permits: StatutoryPermits
    client_dossier_markdown: str
