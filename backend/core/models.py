from sqlalchemy import Column, String, Integer, Text, Boolean
from core.database import Base
from datetime import datetime, timezone

class TaskRun(Base):
    __tablename__ = "task_runs"

    task_id = Column(String, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    format_pref = Column(String, nullable=True)
    output = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String, default="running")
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
