import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import String, Text, ForeignKey, Numeric, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def default_size_bands():
    return [
        {"label":"≤2in","min_cm2":0,"max_cm2":20,"hint":"coin-sized"},
        {"label":"2–4in","min_cm2":21,"max_cm2":80,"hint":"palm-sized"},
        {"label":"4–6in","min_cm2":81,"max_cm2":200,"hint":"half-forearm"},
        {"label":">6in","min_cm2":201,"max_cm2":None,"hint":"large piece"},
    ]

# ---------- Tenants ----------

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=True)
    opening_hours: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="trial")  # trial|active|past_due|canceled
    timezone: Mapped[str] = mapped_column(String, default="Europe/Dublin")
    stripe_customer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String, nullable=True)
    plan: Mapped[str] = mapped_column(String, default="starter")
    has_multiple_artists: Mapped[bool] = mapped_column(Boolean, default=False)

# ---------- Artists ----------

class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Optional overrides; if None, fall back to BotConfig
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    shop_minimum: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    style_multipliers: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    placement_multipliers: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)

# ---------- Users ----------

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String, default="owner")


# ---------- Bot Configuration (per tenant) ----------

class BotConfig(Base):
    __tablename__ = "bot_config"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), unique=True, nullable=False)

    currency: Mapped[str] = mapped_column(String, default="EUR")
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric, nullable=False, default=120)
    shop_minimum: Mapped[Decimal] = mapped_column(Numeric, nullable=False, default=80)
    k_size_factor: Mapped[Decimal] = mapped_column(Numeric, nullable=False, default=0.06)

    # JSON columns – you can make these more specific (e.g., dict[str, float]) if you prefer
    style_multipliers: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    placement_multipliers: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    color_multiplier: Mapped[dict[str, float]] = mapped_column(JSON, default={"Color": 1.15, "Black & grey": 1.0})

    disclaimer: Mapped[str] = mapped_column(Text, default="Final quote after in-person sizing and stencil review.")

    default_unit: Mapped[str] = mapped_column(String, default="in")
    allowed_units: Mapped[list[str]] = mapped_column(JSON, default=["in","cm"])
    size_bands: Mapped[list[dict]] = mapped_column(JSON, default=default_size_bands)

# ---------- Conversation State (per tenant + user) ----------

class ConversationState(Base):
    __tablename__ = "conversation_state"

    # composite primary key (tenant_id + user_id)
    tenant_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)  # Messenger PSID later

    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
