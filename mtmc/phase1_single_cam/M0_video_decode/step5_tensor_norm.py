"""M0 VIDEO DECODE — Step 5/5: Normalize the image matrix into an AI-ready tensor.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def normalize_to_tensor(frame: dt.Frame) -> dt.NDArray:
    """Normalize the image matrix into an AI-ready tensor."""
    raise NotImplementedError("TODO: M0 VIDEO DECODE step 5 — normalize_to_tensor")
