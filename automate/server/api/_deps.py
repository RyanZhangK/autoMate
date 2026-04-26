"""DI helpers for routers."""
from __future__ import annotations

from fastapi import Request

from ..state import AppState


def state(request: Request) -> AppState:
    return request.app.state.app_state
