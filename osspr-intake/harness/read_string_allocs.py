"""Allocation count for Chomper.read_string on a multi-megabyte C string.

Prints one integer: PyObject allocations inside a single read_string call.
The guest buffer holds a repeated JSON record with no interior NUL, just
under 8 MiB, which is the size of a large token or response blob.
"""

from __future__ import annotations

import gc
import logging

import counter

alloccount = counter.load()

logging.disable(logging.CRITICAL)

from chomper import Chomper
from chomper.const import ARCH_ARM64, OS_ANDROID

RECORD = (
    '{"alg":"AES-256-GCM","kid":"mocha","uid":'
    '"00000000-0000-4000-8000-000000000000","n":1}\n'
)
# 8192 reads of the 1024-byte window, with the terminator in the last window.
TARGET = 8192 * 1024 - 64


def build_text() -> str:
    text = (RECORD * ((TARGET // len(RECORD)) + 1))[:TARGET]
    if "\x00" in text or len(text.encode("utf-8")) != len(text):
        raise RuntimeError("workload must be ASCII without NULs")
    return text


def main() -> None:
    text = build_text()
    emu = Chomper(arch=ARCH_ARM64, os_type=OS_ANDROID)

    with emu.memory_scope() as mem:
        address = mem.create_buffer(len(text) + 1)
        emu.write_string(address, text)

        gc.collect()
        gc.disable()
        alloccount.start()
        try:
            result = emu.read_string(address)
        finally:
            count = alloccount.stop()
            gc.enable()

    if result != text:
        raise SystemExit("read_string did not round-trip the guest C string")
    print(count)


if __name__ == "__main__":
    main()
