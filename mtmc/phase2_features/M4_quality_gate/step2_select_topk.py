"""M4 QUALITY GATE — Step 2/2: Keep only the K best crops by quality score.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def select_topk(crops: list[dt.Crop], k: int) -> list[dt.Crop]:
    """Keep only the K best crops by quality score."""
    raise NotImplementedError("TODO: M4 QUALITY GATE step 2 — select_topk")
