"""
FastAPI server for FsExplorer web UI.

Provides a WebSocket endpoint for real-time workflow streaming
and serves the single-page HTML interface.
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .workflow import (
    FsExplorerWorkflow,
    InputEvent,
    ToolCallEvent,
    GoDeeperEvent,
    AskHumanEvent,
    HumanAnswerEvent,
    ExplorationEndEvent,
    WORKFLOW_TIMEOUT_SECONDS,
)
from .agent import FsExplorerAgent

app = FastAPI(title="FsExplorer", description="AI-powered filesystem exploration")


class TaskRequest(BaseModel):
    """Request model for task submission."""
    task: str
    folder: str = "."


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the main UI HTML file."""
    html_path = Path(__file__).parent / "ui.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>UI not found</h1>", status_code=404)


@app.get("/api/folders")
async def list_folders(path: str = "."):
    """
    List folders in the given path.
    Returns list of folder names and current path info.
    """
    try:
        base_path = Path(path).resolve()
        if not base_path.exists():
            return JSONResponse({"error": "Path not found"}, status_code=404)
        if not base_path.is_dir():
            return JSONResponse({"error": "Not a directory"}, status_code=400)
        
        # Get folders (non-hidden)
        folders = sorted([
            f.name for f in base_path.iterdir()
            if f.is_dir() and not f.name.startswith('.')
        ])
        
        # Get parent path (if not at root)
        parent = str(base_path.parent) if base_path != base_path.parent else None
        
        return {
            "current": str(base_path),
            "parent": parent,
            "folders": folders,
            "files_count": len([f for f in base_path.iterdir() if f.is_file()]),
        }
    except PermissionError:
        return JSONResponse({"error": "Permission denied"}, status_code=403)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.websocket("/ws/explore")
async def websocket_explore(websocket: WebSocket):
    """
    WebSocket endpoint for real-time exploration streaming.
    
    Protocol:
    1. Client sends: {"task": "user question"}
    2. Server streams events: {"type": "...", "data": {...}}
    3. Final event: {"type": "complete", "data": {...}}
    """
    await websocket.accept()
    
    try:
        # Receive the task
        data = await websocket.receive_json()
        task = data.get("task", "")
        folder = data.get("folder", ".")
        
        if not task:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "No task provided"}
            })
            return
        
        # Validate folder
        folder_path = Path(folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Invalid folder: {folder}"}
            })
            return
        
        # Instantiate agent for this session
        try:
            agent = FsExplorerAgent(base_directory=str(folder_path))
        except ValueError as e:
            await websocket.send_json({
                "type": "error",
                "data": {"message": str(e)}
            })
            return
        
        # Send start event
        await websocket.send_json({
            "type": "start",
            "data": {"task": task, "folder": str(folder_path)}
        })
        
        # Instantiate and configure workflow for this session
        workflow = FsExplorerWorkflow(timeout=WORKFLOW_TIMEOUT_SECONDS)
        workflow.agent = agent

        # Run the workflow
        step_number = 0
        print("DEBUG: Starting workflow handler...", flush=True)
        try:
            handler = workflow.run(start_event=InputEvent(task=task, base_directory=str(folder_path)))
        except Exception as e:
            print(f"DEBUG: Error creating workflow handler: {e}", flush=True)
            import traceback
            traceback.print_exc()
            raise

        # Stream events
        print("DEBUG: Streaming events...", flush=True)
        async for event in handler.stream_events():
            print(f"DEBUG: Received event: {type(event)}", flush=True)
            if isinstance(event, ToolCallEvent):
                print(f"DEBUG: Streaming ToolCallEvent: {event.tool_name}", flush=True)
                step_number += 1
                await websocket.send_json({
                    "type": "tool_call",
                    "data": {
                        "tool_name": event.tool_name,
                        "tool_input": event.tool_input,
                        "reason": event.reason,
                        "step": step_number
                    }
                })
                
            elif isinstance(event, GoDeeperEvent):
                print("DEBUG: Streaming GoDeeperEvent", flush=True)
                step_number += 1
                await websocket.send_json({
                    "type": "go_deeper",
                    "data": {
                        "directory": event.directory,
                        "reason": event.reason,
                        "step": step_number
                    }
                })
                
            elif isinstance(event, AskHumanEvent):
                print("DEBUG: Streaming AskHumanEvent", flush=True)
                await websocket.send_json({
                    "type": "ask_human",
                    "data": {
                        "question": event.question,
                        "reason": event.reason,
                    }
                })
                
                # Wait for human response
                response_data = await websocket.receive_json()
                print(f"DEBUG: Received human response: {response_data}", flush=True)
                handler.ctx.send_event(
                    HumanAnswerEvent(response=response_data.get("response", ""))
                )
        
        # Get final result
        print("DEBUG: Awaiting final result...", flush=True)
        result = await handler
        print(f"DEBUG: Final result received: {result}", flush=True)
        
        # Get token usage
        usage = agent.token_usage
        input_cost, output_cost, total_cost = usage._calculate_cost()
        
        print("DEBUG: Sending completion message...", flush=True)
        await websocket.send_json({
            "type": "complete",
            "data": {
                "final_result": getattr(result, "final_result", None),
                "error": getattr(result, "error", None),
                "stats": {
                    "steps": step_number,
                    "api_calls": usage.api_calls,
                    "documents_scanned": usage.documents_scanned,
                    "documents_parsed": usage.documents_parsed,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "tool_result_chars": usage.tool_result_chars,
                    "estimated_cost": round(total_cost, 6),
                }
            }
        })
        print("DEBUG: Completion message sent.", flush=True)
        
        # Graceful shutdown delay
        await asyncio.sleep(0.5)
        
    except WebSocketDisconnect:
        print("DEBUG: WebSocket disconnected by client.", flush=True)
        pass
    except Exception as e:
        print(f"DEBUG: Server error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Server error: {str(e)}"}
            })
        except:
            pass
    finally:
        pass


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()

