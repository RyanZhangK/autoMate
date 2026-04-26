"""LLM provider configuration."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...providers import CATALOG, get_spec
from ._deps import state

router = APIRouter(tags=["models"], prefix="/models")


class ProviderUpdate(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    default_model: str | None = None
    enabled: bool | None = None


class ActiveSelection(BaseModel):
    provider_id: str
    model: str | None = None


@router.get("/catalog")
def catalog():
    """Static catalog — what providers we know about."""
    return [{
        "id": p.id, "display_name": p.display_name, "region": p.region,
        "base_url": p.base_url, "api_key_url": p.api_key_url, "docs_url": p.docs_url,
        "models": list(p.models), "requires_key": p.requires_key, "notes": p.notes,
    } for p in CATALOG]


@router.get("")
def list_providers(s=Depends(state)):
    return s.db.list_providers()


@router.get("/active")
def active(s=Depends(state)):
    return {"provider_id": s.providers.active_provider_id(),
            "model": s.providers.active_model()}


@router.post("/active")
def set_active(sel: ActiveSelection, s=Depends(state)):
    if not s.db.get_provider(sel.provider_id):
        raise HTTPException(404, "unknown provider")
    s.providers.set_active_provider(sel.provider_id, sel.model)
    return {"ok": True}


@router.patch("/{provider_id}")
def update_provider(provider_id: str, body: ProviderUpdate, s=Depends(state)):
    spec = get_spec(provider_id)
    if not spec:
        raise HTTPException(404, "unknown provider")
    existing = s.db.get_provider(provider_id) or {}
    s.db.upsert_provider(
        id=provider_id,
        display_name=spec.display_name,
        base_url=body.base_url if body.base_url is not None else existing.get("base_url") or spec.base_url,
        api_key=body.api_key,
        default_model=body.default_model if body.default_model is not None else existing.get("default_model"),
        enabled=body.enabled if body.enabled is not None else bool(existing.get("enabled", True)),
    )
    return s.db.get_provider(provider_id)


@router.post("/{provider_id}/test")
def test_provider(provider_id: str, s=Depends(state)):
    """Cheap smoke test — call the provider with a 1-token reply."""
    from ...providers import ChatMessage
    try:
        client = s.providers.client(provider_id)
        resp = client.chat(
            [ChatMessage(role="user", content="Reply with the single word: OK")],
            model=s.db.get_provider(provider_id)["default_model"],
            max_tokens=8,
        )
        return {"ok": True, "reply": resp.content[:200]}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"{type(e).__name__}: {e}")


@router.delete("/{provider_id}")
def delete_provider(provider_id: str, s=Depends(state)):
    s.db.delete_provider(provider_id)
    return {"ok": True}
