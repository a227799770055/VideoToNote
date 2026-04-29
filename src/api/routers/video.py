from fastapi import APIRouter, BackgroundTasks
import uuid
from typing import Dict, Any

from src.api.schemas.requests import VideoProcessRequest, TaskResponse, TaskStatusResponse
from src.core.processor import VideoProcessor

router = APIRouter(tags=["Video Processing"])

# Mock store for tasks status. In production this should be Redis/DB.
tasks_db: Dict[str, Dict[str, Any]] = {}

def process_video_task(task_id: str, request: VideoProcessRequest):
    tasks_db[task_id]["status"] = "processing"
    
    try:
        # initialize and run the processor
        processor = VideoProcessor(
            model_name=request.model,
            transcriber_type=request.transcriber,
            keep_audio=request.keep_audio,
            language=request.language
        )
        
        result = None
        if request.youtube_url:
            result = processor.process_youtube(request.youtube_url)
        elif request.audio_path:
            result = processor.process_audio(request.audio_path)
            
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = {"file_paths": result}
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


@router.post("/process", response_model=TaskResponse)
async def process_video(request: VideoProcessRequest, background_tasks: BackgroundTasks):
    if not request.youtube_url and not request.audio_path:
        return {"task_id": "", "status": "error", "message": "Either youtube_url or audio_path must be provided."}
        
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "status": "pending",
        "result": None,
        "error": None
    }
    
    background_tasks.add_task(process_video_task, task_id, request)
    
    return TaskResponse(
        task_id=task_id, 
        status="pending", 
        message="Task submitted successfully."
    )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        return TaskStatusResponse(task_id=task_id, status="not_found", error="Task ID not found")
        
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )
