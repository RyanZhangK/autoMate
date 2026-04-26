"""Direct (non-LLM) tool invocation.

Useful when an upstream caller already knows exactly which tool + args it wants
and just needs autoMate's hands.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ._deps import state

router = APIRouter(tags=["execute"], prefix="/execute")


class ExecRequest(BaseModel):
    args: dict = {}


@router.post("/{tool_name}")
def execute(tool_name: str, body: ExecRequest, s=Depends(state)):
    tool = s.registry.get(tool_name)
    if not tool:
        raise HTTPException(404, f"unknown tool: {tool_name}")
    try:
        return {"ok": True, "result": tool.call(body.args)}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")
