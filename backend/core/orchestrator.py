import os
import sqlite3
import uuid
import json
import asyncio
from datetime import datetime, timezone

from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent

DB_PATH = os.path.join(os.path.dirname(__file__), '../../runs.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_runs (
            task_id TEXT PRIMARY KEY,
            task TEXT,
            format_pref TEXT,
            output TEXT,
            score INTEGER,
            feedback TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

class Orchestrator:
    def __init__(self):
        # Initialize SQLite DB
        init_db()
        
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
                await websocket.send_json({
                    "agent": agent_name,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                print(f"[!] WebSocket emission failed: {e}")

    def _save_run(self, task_id, task, format_pref, output, score, feedback, status):
        """Helper to save run to SQLite."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if exists to do an insert or update
        cursor.execute("SELECT task_id FROM task_runs WHERE task_id = ?", (task_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE task_runs
                SET output = ?, score = ?, feedback = ?, status = ?
                WHERE task_id = ?
            """, (output, score, json.dumps(feedback) if feedback else None, status, task_id))
        else:
            cursor.execute("""
                INSERT INTO task_runs (task_id, task, format_pref, output, score, feedback, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, task, format_pref, output, score, json.dumps(feedback) if feedback else None, status, datetime.now(timezone.utc).isoformat()))
        
        conn.commit()
        conn.close()

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
            # Running synchronous agent methods in a threadpool to avoid blocking event loop
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
