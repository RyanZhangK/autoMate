"""Bridge between sync tool handlers and the async browser-extension WebSocket.

The agent loop and tool registry are sync. The extension lives behind an
asyncio WebSocket. ``ExtensionBus`` lets a sync caller fire a command, block
on a ``threading.Event``, and receive the response that the async WS handler
delivers from the loop thread.

Pairing is intentionally trivial: the FastAPI server binds to 127.0.0.1 by
default, so any process that can connect to the WS already has local
privileges. We skip token pairing for v1.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class _Pending:
    event: threading.Event
    result: dict | None = None

    def complete(self, msg: dict) -> None:
        self.result = msg
        self.event.set()


class ExtensionBus:
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._outgoing: asyncio.Queue | None = None
        self._pending: dict[str, _Pending] = {}
        self._lock = threading.Lock()
        self._connected_at: float | None = None
        self._client_info: dict = {}

    # ---------- lifecycle (called from the WS handler thread) ----------

    def attach(self, loop: asyncio.AbstractEventLoop, client_info: dict | None = None) -> None:
        self._loop = loop
        self._outgoing = asyncio.Queue()
        self._connected_at = time.time()
        self._client_info = client_info or {}

    def detach(self) -> None:
        self._connected_at = None
        with self._lock:
            for p in self._pending.values():
                p.complete({"ok": False, "error": "extension disconnected"})
            self._pending.clear()
        self._outgoing = None
        self._loop = None
        self._client_info = {}

    @property
    def connected(self) -> bool:
        return self._connected_at is not None

    @property
    def status(self) -> dict:
        return {
            "connected": self.connected,
            "connected_at": self._connected_at,
            "client": self._client_info,
            "pending": len(self._pending),
        }

    # ---------- async side (WS handler) ----------

    async def next_outgoing(self) -> str:
        assert self._outgoing is not None
        return await self._outgoing.get()

    def deliver(self, msg: dict) -> None:
        cid = msg.get("id")
        with self._lock:
            pending = self._pending.pop(cid, None)
        if pending:
            pending.complete(msg)

    # ---------- sync side (tool handlers) ----------

    def call(self, cmd: str, args: dict | None = None, *, timeout: float = 30.0) -> Any:
        if not self.connected or self._loop is None or self._outgoing is None:
            raise RuntimeError(
                "No browser extension connected. Install the autoMate extension "
                "from chrome://extensions (Load unpacked → ./extension/)."
            )
        cid = uuid.uuid4().hex
        pending = _Pending(event=threading.Event())
        with self._lock:
            self._pending[cid] = pending
        payload = json.dumps({"id": cid, "cmd": cmd, "args": args or {}})
        # Hop onto the event loop to enqueue.
        asyncio.run_coroutine_threadsafe(self._outgoing.put(payload), self._loop)

        if not pending.event.wait(timeout):
            with self._lock:
                self._pending.pop(cid, None)
            raise TimeoutError(f"extension call '{cmd}' timed out after {timeout}s")
        result = pending.result or {}
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "extension error"))
        return result.get("result")


# Process-wide singleton — a single extension instance is the expected case.
bus = ExtensionBus()
