"""Optional Windows-only UI automation for DIALux evo (requires pywinauto)."""
from __future__ import annotations


def open_project(exe_path: str, project_path: str):
    try:
        from pywinauto import Application
    except ImportError as e:
        raise RuntimeError("pywinauto is required (Windows only): pip install pywinauto") from e
    app = Application(backend="uia").start(f'"{exe_path}" "{project_path}"')
    return app
