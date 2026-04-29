from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import health, video

app = FastAPI(
    title="VideoToNote API",
    description="智慧影片轉錄與筆記生成工具 API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(health.router, prefix="/api/v1")
app.include_router(video.router, prefix="/api/v1/video")

@app.get("/")
async def root():
    return {"message": "Welcome to VideoToNote API. Visit /docs for documentation."}
