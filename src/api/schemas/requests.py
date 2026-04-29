from pydantic import BaseModel
from typing import Optional

class VideoProcessRequest(BaseModel):
    youtube_url: Optional[str] = None
    audio_path: Optional[str] = None
    model: str = "openai"
    transcriber: str = "fast"
    language: str = "chinese"
    keep_audio: bool = False

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
