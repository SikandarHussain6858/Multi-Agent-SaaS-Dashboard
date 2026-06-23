from pydantic import BaseModel
from typing import Optional

class TaskRequest(BaseModel):
    task: str
    format_pref: str = "blog"

class TaskResponse(BaseModel):
    task_id: str
    task: str
    format_pref: Optional[str] = None
    output: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    status: str
    created_at: str

    class Config:
        from_attributes = True

class TaskRunResponse(BaseModel):
    task_id: str
    message: str
