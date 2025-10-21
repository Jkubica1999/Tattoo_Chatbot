from app.core.size import to_area_cm2
from app.core.nlu import parse_message
from app.core.estimator import estimate, estimate_from_area
from app.core.pricing import resolve_pricing
from app.models import Artist
from sqlalchemy.orm import Session
from datetime import datetime

REQUIRED_SLOTS = ["style", "placement", "color", "size_band"]

def load_state(db, tenant_id: str, user_id: str) -> dict:
    # TODO: fetch from ConversationState table; fallback to empty
    return {"slots": {}, "last_intent": None}

def save_state(db, tenant_id: str, user_id: str, state: dict):
    # TODO: upsert to DB
    pass

def next_question(missing_key: str) -> str:
    q_map = {
        "style": "What style are you after? (Fine-line, Realism, Traditional, Japanese)",
        "size_band": "About how big? (≤5cm, 6–10cm, 11–15cm, >15cm)",
        "placement": "Where on the body?",
        "color": "Black & grey or color?",
    }
    return q_map[missing_key]

def handle_incoming_text(db, tenant_id: str, user_id: str, text: str | None, attachments: list | None):
    state = load_state(db, tenant_id, user_id)
    slots = state.get("slots", {}).copy()

    # 1) Parse
    parsed = parse_message(text or "")
    for k in ["style","placement","color","size_band"]:
        if parsed.get(k):
            slots[k] = parsed[k]

    # 2) Decide intent (naive: pricing if any of price/quote words OR if we’re mid slot-fill)
    intent = decide_intent(text or "", state)

    # 3) If pricing intent → slot filling
    if intent == "pricing":
        missing = [k for k in REQUIRED_SLOTS if not slots.get(k)]
        if missing:
            ask = next_question(missing[0])
            state.update({"slots": slots, "last_intent": "pricing"})
            save_state(db, tenant_id, user_id, state)
            return ask

        # All slots present → estimate
        hours, low, high = estimate(slots["size_band"], slots["style"], slots["placement"], slots["color"])
        assumptions = f'{slots["style"]}, {slots["size_band"]}, {slots["placement"]}, {slots["color"]}'
        state.update({"slots": {}, "last_intent": None})  # reset for next task
        save_state(db, tenant_id, user_id, state)
        return f"Ballpark: €{low}–€{high} (~{hours}h). Assuming {assumptions}. Want to share a reference photo?"

    # 4) Non-pricing intents (FAQ, hours, aftercare, booking, policies)
    if intent == "aftercare":
        return "After your session, wash gently with unscented soap, pat dry, thin layer of ointment 2–3× a day for a few days. Avoid sun/swimming for ~2 weeks."
    if intent == "hours":
        return "We’re open Tue–Sat, 11:00–19:00. Want to book a consult?"
    if intent == "location":
        return "We’re at 123 Studio St. Tap here for directions: your.link/dir"
    if intent == "booking":
        return "I can help book a consult. What day/time works for you next week?"

    # 5) Fallback
    state.update({"last_intent": None})
    save_state(db, tenant_id, user_id, state)
    return "I can help with pricing, booking, aftercare, or studio info. What would you like to do?"

def decide_intent(text: str, state: dict) -> str:
    t = text.lower()
    if state.get("last_intent") == "pricing":
        return "pricing"
    if any(k in t for k in ["price", "cost", "quote", "how much", "estimate"]):
        return "pricing"
    if any(k in t for k in ["aftercare","heal","healing","wash","ointment"]):
        return "aftercare"
    if any(k in t for k in ["hour","open","close","opening","time"]):
        return "hours"
    if any(k in t for k in ["where","address","located","location"]):
        return "location"
    if any(k in t for k in ["book","appointment","schedule","consult"]):
        return "booking"
    return "fallback"

# -------- Meta send (placeholder) ---------
import os, requests, hashlib, hmac

def to_meta_send(tenant_id: str, psid: str, text: str):
    page_access_token = get_page_token(tenant_id)
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={page_access_token}"
    payload = {"recipient": {"id": psid}, "message": {"text": text}}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def find_artist_by_name(db: Session, tenant_id: str, name_like: str | None):
    if not name_like:
        return None
    name = name_like.strip().lower()
    q = db.query(Artist).filter(Artist.tenant_id == tenant_id, Artist.active == True)
    for a in q.all():
        if name in (a.name or "").lower():
            return a
    return None

def get_page_token(tenant_id: str) -> str:
    # TODO: fetch per-tenant page token from DB/secret store
    return os.getenv("META_PAGE_TOKEN", "")
