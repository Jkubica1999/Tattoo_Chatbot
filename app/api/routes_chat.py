from fastapi import APIRouter, Request, Depends
from app.core.nlu import parse_message
from app.core.estimator import estimate
from app.core.db import get_db

router = APIRouter()

@router.post("/chat")
async def chat(msg: dict, db=Depends(get_db)):
    text = (msg or {}).get("text", "")
    slots = parse_message(text)
    required = ["style", "placement", "color", "size_band"]
    missing = [k for k in required if not slots.get(k)]
    if missing:
        q_map = {
            "style": "What style are you after?",
            "size_band": "About how big? (≤5cm, 6–10cm, 11–15cm, >15cm)",
            "placement": "Where on the body?",
            "color": "Black & grey or color?",
        }
        return {"reply": q_map[missing[0]], "slots": slots}

    hours, low, high = estimate(slots["size_band"], slots["style"], slots["placement"], slots["color"])
    assumptions = f'{slots["style"]}, {slots["size_band"]}, {slots["placement"]}, {slots["color"]}'
    return {"reply": f"Ballpark: €{low}–€{high} (~{hours}h). Assuming {assumptions}. Does that look right?"}
