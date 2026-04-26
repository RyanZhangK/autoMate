from __future__ import annotations

from fastapi import APIRouter, Depends

from ...version import __version__
from ._deps import state

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"ok": True, "version": __version__}


@router.get("/status")
def status(s=Depends(state)):
    return {
        "version": __version__,
        "active_provider": s.providers.active_provider_id(),
        "active_model": s.providers.active_model(),
        "providers": len(s.db.list_providers()),
        "providers_configured": sum(1 for p in s.db.list_providers() if p["api_key_set"]),
        "integrations": len(s.db.list_connections()),
        "integrations_connected": sum(1 for c in s.db.list_connections() if c["status"] == "connected"),
        "tools": len(s.registry.all()),
    }
