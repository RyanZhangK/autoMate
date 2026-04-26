from __future__ import annotations

from fastapi import APIRouter, Depends

from ._deps import state

router = APIRouter(tags=["tools"], prefix="/tools")


@router.get("")
def list_tools(s=Depends(state)):
    grouped: dict[str, list[dict]] = {}
    for t in s.registry.all():
        grouped.setdefault(t.category, []).append({
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
            "requires": t.requires,
            "danger": t.danger,
        })
    return grouped


@router.get("/{tool_name}")
def describe(tool_name: str, s=Depends(state)):
    t = s.registry.get(tool_name)
    if not t:
        return {"error": "not found"}
    return {
        "name": t.name,
        "description": t.description,
        "parameters": t.parameters,
        "category": t.category,
        "requires": t.requires,
        "danger": t.danger,
    }
