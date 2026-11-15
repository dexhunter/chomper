"""Allocation count for Chomper.read_array on a large pointer table.

Prints one integer: PyObject allocations inside a single read_array call.
The table is 16384 little-endian u64 pointers, the same shape read_array
sees for a large relocation or pointer section.
"""

from __future__ import annotations

import gc
import logging
import struct

import counter

alloccount = counter.load()

logging.disable(logging.CRITICAL)

from chomper import Chomper
from chomper.const import ARCH_ARM64, OS_ANDROID

POINTER_COUNT = 16384
BASE = 0x100000000


def main() -> None:
    emu = Chomper(arch=ARCH_ARM64, os_type=OS_ANDROID)
    nbytes = POINTER_COUNT * emu.arch.addr_size
    payload = b"".join(struct.pack("<Q", BASE + index) for index in range(POINTER_COUNT))
    expected = [BASE + index for index in range(POINTER_COUNT)]

    with emu.memory_scope() as mem:
        address = mem.create_buffer(nbytes)
        emu.write_bytes(address, payload)

        gc.collect()
        gc.disable()
        alloccount.start()
        try:
            values = emu.read_array(address, address + nbytes)
        finally:
            count = alloccount.stop()
            gc.enable()

    if values != expected:
        raise SystemExit("read_array returned unexpected pointer values")
    print(count)


if __name__ == "__main__":
    main()
