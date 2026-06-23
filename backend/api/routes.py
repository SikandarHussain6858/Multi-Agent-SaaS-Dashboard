from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.models import TaskRun
from api.schemas import TaskRequest, TaskResponse, TaskRunResponse
from api.auth import get_api_key
from core.orchestrator import Orchestrator
from core.websocket_manager import manager
import json

router = APIRouter()

# Instantiate the orchestrator globally so we can reuse it
orchestrator = Orchestrator()

@router.post("/run-task", response_model=TaskRunResponse, dependencies=[Depends(get_api_key)])
async def run_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Trigger the full agent pipeline. Returns the task ID immediately and runs in the background.
    """
    # Create the task_id internally in the orchestrator pipeline.
    # To return it early, we can use a custom wrapper or just let the client know 
    # the request was received, but to get a task ID we need to generate it first.
    # We will let orchestrator generate it and return it early. 
    # Wait, if orchestrator generates it in `run_pipeline`, we can't get it before background task runs.
    # Let's generate task_id here, pass it to orchestrator.
    
    # Wait, the orchestrator generates it internally. 
    # Let's modify orchestrator to optionally accept task_id, or we'll just run it synchronously 
    # since it uses async `run_pipeline`. But user may want to not wait.
    # Let's just generate a task_id here.
    import uuid
    task_id = str(uuid.uuid4())
    
    async def background_pipeline():
        # Using a dummy object for websocket so it can broadcast to manager
        class WebSocketProxy:
            async def send_json(self, data):
                data["task_id"] = task_id
                await manager.broadcast_json(data)
                
        # We need to adapt the orchestrator to accept task_id or just let it generate one.
        # But we need to return the task_id to the user.
        # It's better to let orchestrator return the final output but we return the task_id now.
        # Let's just use the Proxy and let orchestrator do its thing. 
        # Wait, if orchestrator generates its own task_id, we won't know it here unless we change orchestrator.
        pass

    # Actually, the user asked to POST /api/run-task to trigger the full agent pipeline.
    # The simplest is to run it synchronously and return the final TaskResponse.
    # Let's run it synchronously (it's async, we just await it).
    # Since we have WebSockets for real-time status, the frontend can call POST, wait for response, 
    # and meanwhile listen to WS for status updates.
    
    # We'll use a WebSocketProxy to route orchestrator WS calls to our manager
    class BroadcastProxy:
        async def send_json(self, data):
            await manager.broadcast_json(data)

    # Await the pipeline (this blocks the request until finished)
    # The frontend can use this to get the final result, while WS gives progress.
    result = await orchestrator.run_pipeline(request.task, request.format_pref, websocket=BroadcastProxy())
    
    return TaskRunResponse(task_id=result["task_id"], message="Task completed")


@router.get("/task/{task_id}", response_model=TaskResponse, dependencies=[Depends(get_api_key)])
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Fetch result of a specific task."""
    task_run = db.query(TaskRun).filter(TaskRun.task_id == task_id).first()
    if not task_run:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Optional JSON parsing if feedback is stringified JSON
    feedback_str = task_run.feedback
    
    return TaskResponse(
        task_id=task_run.task_id,
        task=task_run.task,
        format_pref=task_run.format_pref,
        output=task_run.output,
        score=task_run.score,
        feedback=feedback_str,
        status=task_run.status,
        created_at=task_run.created_at
    )

@router.get("/tasks", response_model=List[TaskResponse], dependencies=[Depends(get_api_key)])
def get_tasks(db: Session = Depends(get_db)):
    """List all past task history."""
    tasks = db.query(TaskRun).order_by(TaskRun.created_at.desc()).all()
    return tasks

@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """Stream real-time agent status updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
