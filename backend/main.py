from fastapi import FastAPI

from database import engine, Base
import models

from routers.products import router as products_router
from routers.assistant import router as assistant_router


app = FastAPI(
    title="AI Shopping Assistant",
    description="An AI-powered shopping assistant and recommendation system.",
    version="1.0.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Register routers
app.include_router(products_router)
app.include_router(assistant_router)


@app.get("/")
def home():
    return {
        "message": "AI Shopping Assistant is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }