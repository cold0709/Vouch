# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import brand_kit, check, content, review, insights

app = FastAPI(title="Vouch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brand_kit.router, prefix="/api/brand-kit", tags=["brand-kit"])
app.include_router(check.router, prefix="/api/check", tags=["check"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])


@app.get("/")
def root():
    return {"message": "Vouch API is running"}