import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    status = Column(String, default="trial")  # trial|active|past_due|canceled
    timezone = Column(String, default="Europe/Dublin")
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    plan = Column(String, default="starter")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String, default="owner")

class BotConfig(Base):
    __tablename__ = "bot_config"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), unique=True, nullable=False)
    currency = Column(String, default="EUR")
    hourly_rate = Column(Numeric, nullable=False, default=120)
    shop_minimum = Column(Numeric, nullable=False, default=80)
    k_size_factor = Column(Numeric, nullable=False, default=0.06)
    style_multipliers = Column(JSON, default={})
    placement_multipliers = Column(JSON, default={})
    color_multiplier = Column(JSON, default={"Color":1.15,"Black & grey":1.0})
    disclaimer = Column(Text, default="Final quote after in-person sizing and stencil review.")
