"""Natural-language entry point.

POST /api/agent/run    — synchronous run (blocks until the agent loop ends).
WS   /api/sessions/ws  — streaming variant lives in sessions.py.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ._deps import state

router = APIRouter(tags=["agent"], prefix="/agent")


class RunRequest(BaseModel):
    prompt: str
    model: str | None = None
    allowed_tools: list[str] | None = None
    source: str = "web"


@router.post("/run")
def run(body: RunRequest, s=Depends(state)):
    if not body.prompt.strip():
        raise HTTPException(400, "prompt is required")
    try:
        result = s.agent.run(
            body.prompt, source=body.source, model=body.model,
            allowed_tools=body.allowed_tools,
        )
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return {
        "id": result.id,
        "final": result.final,
        "events": [{"kind": e.kind, "payload": e.payload} for e in result.events],
    }


@router.get("/runs")
def list_runs(s=Depends(state), limit: int = 50):
    return s.db.list_runs(limit=limit)
