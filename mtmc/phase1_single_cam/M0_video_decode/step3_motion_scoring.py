"""M0 VIDEO DECODE — Step 3/5: Score how much changed vs the previous frame.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def score_motion(frame: dt.Frame, prev: Optional[dt.Frame]) -> float:
    """Score how much changed vs the previous frame."""
    raise NotImplementedError("TODO: M0 VIDEO DECODE step 3 — score_motion")
