"""Headless / headed browser control via Playwright.

A single persistent browser context is reused across tool calls so cookies and
logins survive between actions in the same session. The Playwright import is
lazy because installing browsers (~300MB) is optional.
"""
from __future__ import annotations

import threading
from typing import Any

from .registry import Tool, ToolRegistry


_lock = threading.Lock()
_state: dict[str, Any] = {"playwright": None, "browser": None, "context": None, "page": None}


def _ensure_page(headless: bool = False):
    with _lock:
        if _state["page"]:
            return _state["page"]
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise RuntimeError(
                "Playwright is not installed. Run: pip install 'autoMate[browser]' "
                "and then 'python -m playwright install chromium'."
            ) from e
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=headless)
        ctx = browser.new_context()
        page = ctx.new_page()
        _state.update({"playwright": pw, "browser": browser, "context": ctx, "page": page})
        return page


def _close():
    with _lock:
        for k in ("page", "context", "browser"):
            obj = _state.get(k)
            if obj:
                try:
                    obj.close()
                except Exception:  # noqa: BLE001
                    pass
        pw = _state.get("playwright")
        if pw:
            try:
                pw.stop()
            except Exception:  # noqa: BLE001
                pass
        for k in ("page", "context", "browser", "playwright"):
            _state[k] = None


def register(reg: ToolRegistry) -> None:
    reg.register(Tool(
        name="browser.open",
        description="Open a URL in a managed Chromium tab. Reuses one page across calls.",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "headless": {"type": "boolean", "default": False},
            },
            "required": ["url"],
        },
        handler=lambda url, headless=False: (
            (lambda p: {"url": p.url, "title": p.title()})(
                (_ensure_page(headless), _state["page"].goto(url, wait_until="domcontentloaded"), _state["page"])[2]
            )
        ),
        category="browser",
        danger="medium",
    ))

    def _click(selector: str) -> dict:
        page = _ensure_page()
        page.locator(selector).first.click()
        return {"clicked": selector, "url": page.url}

    reg.register(Tool(
        name="browser.click",
        description="Click the first element matching a CSS selector or Playwright text= locator.",
        parameters={
            "type": "object",
            "properties": {"selector": {"type": "string"}},
            "required": ["selector"],
        },
        handler=_click,
        category="browser",
        danger="medium",
    ))

    def _type(selector: str, text: str, submit: bool = False) -> dict:
        page = _ensure_page()
        loc = page.locator(selector).first
        loc.fill(text)
        if submit:
            loc.press("Enter")
        return {"typed_into": selector, "url": page.url}

    reg.register(Tool(
        name="browser.type",
        description="Fill a form field. Set submit=true to press Enter after typing.",
        parameters={
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "text": {"type": "string"},
                "submit": {"type": "boolean", "default": False},
            },
            "required": ["selector", "text"],
        },
        handler=_type,
        category="browser",
        danger="medium",
    ))

    def _extract(selector: str | None = None, kind: str = "text") -> dict:
        page = _ensure_page()
        if not selector:
            return {"url": page.url, "title": page.title(), "text": page.locator("body").inner_text()[:8000]}
        loc = page.locator(selector)
        if kind == "html":
            return {"items": [el.inner_html() for el in loc.element_handles()][:50]}
        if kind == "attribute":
            return {"items": [el.get_attribute("href") or el.get_attribute("src") for el in loc.element_handles()][:50]}
        return {"items": [el.inner_text() for el in loc.element_handles()][:50]}

    reg.register(Tool(
        name="browser.extract",
        description=(
            "Pull text/html/links from the current page. Pass no selector to grab the "
            "whole body text (truncated to 8KB)."
        ),
        parameters={
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "kind": {"type": "string", "enum": ["text", "html", "attribute"], "default": "text"},
            },
        },
        handler=_extract,
        category="browser",
    ))

    def _screenshot(full_page: bool = False) -> dict:
        import base64
        page = _ensure_page()
        png = page.screenshot(full_page=full_page)
        return {"format": "png", "base64": base64.b64encode(png).decode()}

    reg.register(Tool(
        name="browser.screenshot",
        description="Capture the current page (PNG, base64-encoded).",
        parameters={"type": "object", "properties": {"full_page": {"type": "boolean", "default": False}}},
        handler=_screenshot,
        category="browser",
    ))

    reg.register(Tool(
        name="browser.close",
        description="Close the managed browser and free its resources.",
        parameters={"type": "object", "properties": {}},
        handler=lambda: (_close(), {"closed": True})[1],
        category="browser",
    ))
