from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.image import router as image_router


app = FastAPI(
    title="AIPicture API",
    description="AI Image Editing API powered by Stability AI",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(image_router)


@app.get("/")
async def root():
    return {
        "message": "AIPicture API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }