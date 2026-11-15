"""Runtime of ELFLoader._load_symbols on the Android arm64 libc used by tests.

Prints one float: milliseconds spent inside _load_symbols, excluding emulator
startup and ELF open.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

logging.disable(logging.CRITICAL)

from elftools.elf.elffile import ELFFile

from chomper import Chomper
from chomper.const import ARCH_ARM64, OS_ANDROID

LIBC = (
    Path(__file__).resolve().parents[2]
    / "rootfs"
    / "android"
    / "system"
    / "lib64"
    / "libc.so"
)
MODULE_BASE = 0x10000000


def main() -> None:
    if not LIBC.is_file():
        raise SystemExit(f"missing Android libc fixture: {LIBC}")

    emu = Chomper(arch=ARCH_ARM64, os_type=OS_ANDROID)
    loader = emu.os.loader

    with ELFFile.load_from_path(str(LIBC)) as elffile:
        started = time.perf_counter()
        symbols = loader._load_symbols(elffile, MODULE_BASE)
        elapsed_ms = (time.perf_counter() - started) * 1000.0

    names = {symbol.name for symbol in symbols}
    if "malloc" not in names or "strlen" not in names or len(symbols) < 1000:
        raise SystemExit("unexpected dynsym export set from libc.so")
    malloc = next(symbol for symbol in symbols if symbol.name == "malloc")
    if malloc.address <= MODULE_BASE:
        raise SystemExit("malloc address was not rebased")
    print(f"{elapsed_ms:.6f}")


if __name__ == "__main__":
    main()
