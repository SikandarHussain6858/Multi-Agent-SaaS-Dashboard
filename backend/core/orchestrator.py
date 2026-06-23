import os
import uuid
import json
import asyncio
from datetime import datetime, timezone

from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent

from core.database import SessionLocal, Base, engine
from core.models import TaskRun

class Orchestrator:
    def __init__(self):
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Initialize Agents
        print("[*] Initializing Agents...")
        self.research_agent = ResearchAgent()
        self.writer_agent = WriterAgent()
        self.reviewer_agent = ReviewerAgent()
        print("[*] Agents Initialized successfully.")

    async def _emit_status(self, websocket, agent_name: str, status: str, message: str = ""):
        """Helper to emit WebSocket events safely."""
        if websocket:
            try:
                # If it's a raw WebSocket, we use send_json
                if hasattr(websocket, "send_json"):
                    await websocket.send_json({
                        "agent": agent_name,
                        "status": status,
                        "message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            except Exception as e:
                print(f"[!] WebSocket emission failed: {e}")

    def _save_run(self, task_id, task, format_pref, output, score, feedback, status):
        """Helper to save run to DB using SQLAlchemy."""
        db = SessionLocal()
        try:
            db_run = db.query(TaskRun).filter(TaskRun.task_id == task_id).first()
            feedback_str = json.dumps(feedback) if feedback else None
            
            if db_run:
                db_run.output = output
                db_run.score = score
                db_run.feedback = feedback_str
                db_run.status = status
            else:
                db_run = TaskRun(
                    task_id=task_id,
                    task=task,
                    format_pref=format_pref,
                    output=output,
                    score=score,
                    feedback=feedback_str,
                    status=status
                )
                db.add(db_run)
            db.commit()
        except Exception as e:
            print(f"[!] DB Save Error: {e}")
        finally:
            db.close()

    async def run_pipeline(self, task: str, format_pref: str = "blog", websocket=None) -> dict:
        """
        Runs the full multi-agent pipeline:
        Research -> Writer -> Reviewer
        Emits WebSocket events along the way.
        """
        task_id = str(uuid.uuid4())
        self._save_run(task_id, task, format_pref, "", 0, "", "running")
        
        try:
            # 1. Research Agent
            await self._emit_status(websocket, "Research Agent", "started", "Gathering information...")
            research_summary = await asyncio.to_thread(self.research_agent.run, task)
            
            if "[!] Error" in research_summary:
                raise Exception(f"Research Agent Failed: {research_summary}")
                
            await self._emit_status(websocket, "Research Agent", "completed", "Research complete.")

            # 2. Writer Agent
            await self._emit_status(websocket, "Writer Agent", "started", f"Writing content as {format_pref}...")
            draft_content = await asyncio.to_thread(self.writer_agent.run, research_summary, format_pref)
            
            if "[!] Error" in draft_content:
                raise Exception(f"Writer Agent Failed: {draft_content}")
                
            await self._emit_status(websocket, "Writer Agent", "completed", "Draft created.")

            # 3. Reviewer Agent
            await self._emit_status(websocket, "Reviewer Agent", "started", "Reviewing content for quality...")
            review_result = await asyncio.to_thread(self.reviewer_agent.run, draft_content)
            
            if "error" in review_result and review_result.get("score") == 0:
                raise Exception(f"Reviewer Agent Failed: {review_result.get('error')}")
                
            await self._emit_status(websocket, "Reviewer Agent", "completed", "Review complete.")
            await self._emit_status(websocket, "Orchestrator", "completed", "Pipeline finished successfully.")

            # Prepare final response
            final_output = {
                "task_id": task_id,
                "output": draft_content,
                "score": review_result.get("score", 0),
                "feedback": review_result.get("feedback", ""),
                "approved": review_result.get("approved", False),
                "status": "completed"
            }
            
            # Update DB with final result
            self._save_run(
                task_id=task_id,
                task=task,
                format_pref=format_pref,
                output=draft_content,
                score=final_output["score"],
                feedback=final_output["feedback"],
                status="completed"
            )
            
            return final_output

        except Exception as e:
            error_msg = str(e)
            print(f"[!] Pipeline Error: {error_msg}")
            await self._emit_status(websocket, "Orchestrator", "error", error_msg)
            
            final_output = {
                "task_id": task_id,
                "output": "",
                "score": 0,
                "feedback": error_msg,
                "approved": False,
                "status": "error"
            }
            
            # Update DB with error state
            self._save_run(
                task_id=task_id,
                task=task,
                format_pref=format_pref,
                output="",
                score=0,
                feedback=error_msg,
                status="error"
            )
            
            return final_output

if __name__ == "__main__":
    # Simple test for orchestrator without websocket
    async def test():
        print("--- Testing Orchestrator ---")
        try:
            orchestrator = Orchestrator()
            result = await orchestrator.run_pipeline("Latest updates in fusion energy 2024", "blog")
            print("\n=== Pipeline Result ===")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Failed to run orchestrator test: {e}")
            
    asyncio.run(test())
