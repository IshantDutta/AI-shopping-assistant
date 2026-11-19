from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # Registers SQLAlchemy models before table creation.
from routers.products import router as products_router
from routers.assistant import router as assistant_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShopMate AI",
    description="Hybrid AI shopping assistant with a local product catalog and optional live shopping search.",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(assistant_router)


@app.get("/")
def home():
    return {"name": "ShopMate AI", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
