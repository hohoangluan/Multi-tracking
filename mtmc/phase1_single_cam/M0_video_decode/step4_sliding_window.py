"""M0 VIDEO DECODE — Step 4/5: Pick the best 15 frames per second from the buffer.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def sliding_window_select(frames: list[dt.Frame], scores: list[float], p: cfg.RealtimeParams) -> list[dt.Frame]:
    """Pick the best 15 frames per second from the buffer."""
    raise NotImplementedError("TODO: M0 VIDEO DECODE step 4 — sliding_window_select")
