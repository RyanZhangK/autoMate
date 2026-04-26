"""Native desktop control: screenshot, mouse, keyboard.

Wraps pyautogui (which is already a project dep). Visual element parsing is
delegated to the cloud_vision module where available — kept optional so headless
servers without a display can still expose API integrations.
"""
from __future__ import annotations

import base64
import io
from typing import Any

from .registry import Tool, ToolRegistry


def _has_display() -> bool:
    try:
        import pyautogui  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


def _screenshot(region: list[int] | None = None) -> dict:
    import pyautogui
    img = pyautogui.screenshot(region=tuple(region) if region else None)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {"format": "png", "base64": base64.b64encode(buf.getvalue()).decode(),
            "width": img.width, "height": img.height}


def _click(x: int, y: int, button: str = "left") -> dict:
    import pyautogui
    pyautogui.click(x=x, y=y, button=button)
    return {"clicked": [x, y], "button": button}


def _type(text: str, interval: float = 0.02) -> dict:
    import pyautogui
    pyautogui.typewrite(text, interval=interval)
    return {"typed": text}


def _press(key: str) -> dict:
    import pyautogui
    pyautogui.press(key)
    return {"pressed": key}


def _size() -> dict:
    import pyautogui
    w, h = pyautogui.size()
    return {"width": w, "height": h}


def register(reg: ToolRegistry) -> None:
    if not _has_display():
        # Headless server: skip desktop tools entirely so they don't show up in the catalog.
        return

    reg.register(Tool(
        name="desktop.screenshot",
        description="Capture the screen (full or a [x, y, w, h] region) as base64 PNG.",
        parameters={
            "type": "object",
            "properties": {"region": {"type": "array", "items": {"type": "integer"}}},
        },
        handler=_screenshot,
        category="desktop",
    ))
    reg.register(Tool(
        name="desktop.click",
        description="Click at absolute screen coordinates.",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"},
            },
            "required": ["x", "y"],
        },
        handler=_click,
        category="desktop",
        danger="medium",
    ))
    reg.register(Tool(
        name="desktop.type",
        description="Type a string at the focused element.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}, "interval": {"type": "number", "default": 0.02}},
            "required": ["text"],
        },
        handler=_type,
        category="desktop",
        danger="medium",
    ))
    reg.register(Tool(
        name="desktop.press",
        description="Press a single key (e.g. 'enter', 'tab', 'esc', 'cmd').",
        parameters={
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
        handler=_press,
        category="desktop",
        danger="medium",
    ))
    reg.register(Tool(
        name="desktop.size",
        description="Return the primary screen size in pixels.",
        parameters={"type": "object", "properties": {}},
        handler=_size,
        category="desktop",
    ))
