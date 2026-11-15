"""Build and load the PyObject allocation counter next to this file."""

from __future__ import annotations

import importlib.util
import subprocess
import sysconfig
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SRC = _HERE / "alloccount.c"
_SO = _HERE / "alloccount.so"


def load():
    """Return the alloccount module, compiling it on first use."""
    if not _SO.exists() or _SO.stat().st_mtime < _SRC.stat().st_mtime:
        include = sysconfig.get_config_var("INCLUDEPY")
        if not include:
            raise RuntimeError("Python development headers are required to build alloccount")
        subprocess.check_call(
            [
                "gcc",
                "-shared",
                "-fPIC",
                "-O2",
                f"-I{include}",
                "-o",
                str(_SO),
                str(_SRC),
            ],
            stdout=subprocess.DEVNULL,
        )

    spec = importlib.util.spec_from_file_location("alloccount", _SO)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {_SO}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
