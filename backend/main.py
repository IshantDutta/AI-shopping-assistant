import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401 - registers SQLAlchemy models
from routers.products import router as products_router
from routers.assistant import router as assistant_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShopMate AI",
    description="A hybrid AI shopping assistant powered by Gemini, a local catalog and optional live shopping search.",
    version="2.0.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(assistant_router)


@app.get("/")
def home():
    return {
        "name": "ShopMate AI",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
