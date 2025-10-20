# app/main.py
from dotenv import load_dotenv
load_dotenv() 
from fastapi import FastAPI
from app.api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Tattoo Bot SaaS (MVP)")

    # All versioned/internal endpoints under /api
    app.include_router(api_router)


    @app.get("/health")
    def health():
        return {"ok": True}

    return app

app = create_app()
