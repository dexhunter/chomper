"""Runtime of MemoryManager.alloc for a burst of small blocks.

Prints one float: milliseconds to satisfy 8192 allocations of 16 bytes.
That fills the 16-byte pool (minimum pool 64 KiB, 4096 blocks) and a second
pool, which is the pattern of hook_malloc for many short guest buffers.
"""

from __future__ import annotations

import time

from unicorn import UC_ARCH_ARM64, UC_MODE_ARM, Uc

from chomper.const import HEAP_ADDRESS, MINIMUM_POOL_SIZE
from chomper.memory import MemoryManager

ALLOCATIONS = 8192
BLOCK = 16


def main() -> None:
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    manager = MemoryManager(uc, HEAP_ADDRESS, MINIMUM_POOL_SIZE)
    addresses = [0] * ALLOCATIONS

    started = time.perf_counter()
    for index in range(ALLOCATIONS):
        addresses[index] = manager.alloc(BLOCK)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    if len(set(addresses)) != ALLOCATIONS:
        raise SystemExit("alloc returned a duplicate address")
    if any(address < HEAP_ADDRESS for address in addresses):
        raise SystemExit("alloc returned an address outside the heap")
    if not (addresses[0] < addresses[1] < addresses[-1]):
        raise SystemExit("alloc did not hand out ascending first-fit addresses")
    print(f"{elapsed_ms:.6f}")


if __name__ == "__main__":
    main()
