# app/core/pricing.py
from typing import Optional, Tuple
from app.models import BotConfig, Artist

def resolve_pricing(cfg: BotConfig, artist: Optional[Artist]) -> Tuple[float, float, dict, dict]:
    """Pick artist overrides if present; otherwise use tenant defaults."""
    rate = float(artist.hourly_rate) if (artist and artist.hourly_rate) else float(cfg.hourly_rate)
    shop_min = float(artist.shop_minimum) if (artist and artist.shop_minimum) else float(cfg.shop_minimum)
    style_mul = {**(cfg.style_multipliers or {}), **((artist.style_multipliers or {}) if artist else {})}
    place_mul = {**(cfg.placement_multipliers or {}), **((artist.placement_multipliers or {}) if artist else {})}
    return rate, shop_min, style_mul, place_mul
