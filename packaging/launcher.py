"""PyInstaller entry point.

``automate/__main__.py`` uses ``from .cli import main`` which assumes a
package context. PyInstaller treats the entry script as a top-level module,
so we wrap with an absolute import here.
"""
from automate.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
