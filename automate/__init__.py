"""autoMate — a scheduling hub that gives any LLM hands.

Browser-server architecture. Other AI assistants (Claude Code, Kimi K2, Cursor,
Cline...) call autoMate via MCP or HTTP; autoMate plans, picks tools, fills in
parameters, and executes against the local machine, browsers, and 30+ SaaS APIs.
"""

from .version import __version__

__all__ = ["__version__"]
