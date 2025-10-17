from fastapi import APIRouter
from .routes_chat import router as chat_router
from .routes_estimate import router as estimate_router
from .routes_webhooks import router as webhooks_router 

router = APIRouter(prefix="/api")
router.include_router(chat_router, tags=["chat"])
router.include_router(estimate_router, tags=["estimate"])
router.include_router(webhooks_router, tags=["webhooks"])