# app/core/contracts.py
from typing import Literal, Optional, TypedDict
from pydantic import BaseModel, Field

# ----- Enumerations used by the bot today -----
SizeBand = Literal["≤5cm", "6–10cm", "11–15cm", ">15cm"]
ColorOpt = Literal["Black & grey", "Color"]
Intent = Literal["pricing", "aftercare", "hours", "location", "booking", "fallback"]

# ----- 1) NLU result -----
class Slots(BaseModel):
    style: Optional[str] = None        # keep open set for now (Fine-line, Realism, etc.)
    placement: Optional[str] = None    # e.g. Forearm, Ribs, Hand, Back, Neck, Face...
    color: Optional[ColorOpt] = None
    size_band: Optional[SizeBand] = None

class NLUResult(BaseModel):
    intent: Intent
    slots: Slots
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    needs_followup: bool
    followup_key: Optional[Literal["style", "size_band", "placement", "color"]] = None

# JSON Schema (dict) for LLM “JSON mode” or client-side validation
NLU_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {"enum": ["pricing","aftercare","hours","location","booking","fallback"]},
        "slots": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "style": {"type": ["string","null"]},
                "placement": {"type": ["string","null"]},
                "color": {"enum": ["Black & grey","Color", None]},
                "size_band": {"enum": ["≤5cm","6–10cm","11–15cm",">15cm", None]},
            },
            "required": ["style","placement","color","size_band"]
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "needs_followup": {"type": "boolean"},
        "followup_key": {
            "enum": ["style","size_band","placement","color", None]
        }
    },
    "required": ["intent","slots","confidence","needs_followup","followup_key"]
}

# ----- 2) Reply result -----
class ReplyPolicy(BaseModel):
    used_prices: bool = Field(..., description="Must be true when prices were provided in context.")
    asked_only_one_followup: bool = True
    escalation: bool = False
    escalation_reason: Optional[str] = None

class ReplyResult(BaseModel):
    reply: str
    policy: ReplyPolicy

REPLY_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reply": {"type": "string"},
        "policy": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "used_prices": {"type": "boolean"},
                "asked_only_one_followup": {"type": "boolean"},
                "escalation": {"type": "boolean"},
                "escalation_reason": {"type": ["string","null"]},
            },
            "required": ["used_prices","asked_only_one_followup","escalation","escalation_reason"]
        }
    },
    "required": ["reply","policy"]
}
