"""Re-export the tool registry as a FastMCP server.

So a Claude Desktop / Cursor / Cline / Kimi instance can mount autoMate as an
MCP server and immediately get every shell / browser / SaaS tool, plus a
top-level ``automate`` tool that runs the full agent loop.
"""
from __future__ import annotations

import json
from typing import Any

from .state import build_state


def serve_stdio() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        raise SystemExit("Install with: pip install 'autoMate[mcp]' (mcp[cli] required)") from e

    state = build_state()
    mcp = FastMCP("autoMate")

    # 1) Top-level autonomous mode: NL prompt → agent loop.
    @mcp.tool()
    def automate(prompt: str) -> str:
        """Run an autoMate agent loop from a natural-language prompt.

        autoMate plans, picks tools, fills in parameters, executes, and returns
        the final answer. Best when you want autoMate to figure out the steps."""
        try:
            result = state.agent.run(prompt, source="mcp")
        except RuntimeError as e:
            return f"autoMate error: {e}"
        return result.final or "(no final answer)"

    # 2) Direct tool invocation: surface every registered tool individually.
    for tool in state.registry.all():
        _wrap_tool_for_mcp(mcp, tool)

    mcp.run()


def _wrap_tool_for_mcp(mcp, tool) -> None:
    """Register a registry Tool with FastMCP using a generic kwargs handler."""
    def handler(**kwargs: Any) -> str:  # noqa: ANN401
        try:
            result = tool.call(kwargs)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"error": f"{type(e).__name__}: {e}"})
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False, default=str)

    handler.__name__ = tool.name.replace(".", "_").replace("-", "_")
    handler.__doc__ = tool.description
    # FastMCP infers schema from the wrapper's signature; we accept **kwargs and
    # rely on the LLM-side schema (provided by the registry). Most clients accept
    # this; if a client requires strict schema, we'd codegen typed wrappers.
    mcp.tool()(handler)
