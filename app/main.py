from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.core.estimator import estimate
from app.core.nlu import parse_message

app = FastAPI(title="Tattoo Bot SaaS (MVP)")

@app.get("/health")
def health():
    return {"ok": True}

class EstReq(BaseModel):
    size_band: str
    style: str
    placement: str
    color: str
    rate: float | None = None
    shop_min: float | None = None

@app.post("/api/estimate")
def api_estimate(req: EstReq):
    hours, low, high = estimate(
        req.size_band, req.style, req.placement, req.color,
        rate=req.rate or 120.0, shop_min=req.shop_min or 80.0
    )
    return {"hours": hours, "price_low": low, "price_high": high}

@app.post("/api/chat")
async def chat(msg: dict):
    text = (msg or {}).get("text", "")
    slots = parse_message(text)
    required = ["style", "placement", "color", "size_band"]
    missing = [k for k in required if not slots.get(k)]
    if missing:
        q_map = {
            "style": "What style are you after? (Fine-line, Realism, Traditional, Japanese)",
            "size_band": "About how big? (≤5cm, 6–10cm, 11–15cm, >15cm)",
            "placement": "Where on the body? (forearm, ribs, calf, back, hand)",
            "color": "Black & grey or color?"
        }
        ask = q_map[missing[0]]
        return {"reply": ask, "slots": slots}
    hours, low, high = estimate(slots["size_band"], slots["style"], slots["placement"], slots["color"])
    assumptions = f'{slots["style"]}, {slots["size_band"]}, {slots["placement"]}, {slots["color"]}'
    return {"reply": f"Ballpark: €{low}–€{high} (~{hours}h). Assuming {assumptions}. Does that look right?"}

@app.get("/webhook/meta")
def meta_verify(hub_mode: str | None = None, hub_challenge: str | None = None, hub_verify_token: str | None = None):
    # TODO: validate hub_verify_token
    if hub_mode == "subscribe" and hub_challenge:
        try:
            return int(hub_challenge)
        except Exception:
            return hub_challenge
    return 0

@app.post("/webhook/meta")
async def meta_receive(req: Request):
    body = await req.json()
    # TODO: parse entry.events, resolve tenant by page_id, map to chat()
    return {"ok": True}

@app.post("/webhook/stripe")
async def stripe_webhook(req: Request):
    # TODO: verify signature & handle events
    return {"received": True}
