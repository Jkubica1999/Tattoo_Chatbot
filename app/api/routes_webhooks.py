from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.db import get_db
from app.core.chat_service import handle_incoming_text, to_meta_send

router = APIRouter()

@router.get("/meta")
def meta_verify(hub_mode: str | None = None, hub_challenge: str | None = None, hub_verify_token: str | None = None):
    # TODO: check hub_verify_token against your env
    if hub_mode == "subscribe" and hub_challenge:
        try:
            return int(hub_challenge)
        except Exception:
            return hub_challenge
    raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/meta")
async def meta_receive(req: Request, db=Depends(get_db)):
    body = await req.json()
    # Typical shape: { "object": "page", "entry": [ { "id": "<page_id>", "messaging":[{...}] } ] }
    for entry in body.get("entry", []):
        page_id = entry.get("id")
        tenant_id = resolve_tenant(page_id, db)  # implement mapping
        for m in entry.get("messaging", []):
            psid = m.get("sender", {}).get("id")
            if "message" in m:
                msg = m["message"]
                text = msg.get("text")
                attachments = msg.get("attachments", [])
                # Normalize and route to chat
                reply = handle_incoming_text(db, tenant_id=tenant_id, user_id=psid, text=text, attachments=attachments)
                # Send back to Meta
                to_meta_send(tenant_id=tenant_id, psid=psid, text=reply)
    return {"ok": True}

def resolve_tenant(page_id: str, db):
    # TODO: look up page_id -> tenant_id mapping from DB/config
    return page_id  # naive placeholder
