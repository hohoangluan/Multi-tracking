"""M2 PERSON DETECT — Step 2/3: Suppress overlapping boxes via NMS.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def non_max_suppression(boxes: list[dt.BBox], iou_thr: float) -> list[dt.BBox]:
    """Suppress overlapping boxes via NMS."""
    raise NotImplementedError("TODO: M2 PERSON DETECT step 2 — non_max_suppression")
