"""M0 VIDEO DECODE — Step 2/5: Crop the region of interest and resize to the AI input size.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def select_roi_and_resize(frame: dt.Frame, p: cfg.RealtimeParams) -> dt.Frame:
    """Crop the region of interest and resize to the AI input size."""
    raise NotImplementedError("TODO: M0 VIDEO DECODE step 2 — select_roi_and_resize")
