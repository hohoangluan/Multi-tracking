"""M2 PERSON DETECT — Step 3/3: Drop low-confidence boxes and wrap as detections.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def filter_confidence(boxes: list[dt.BBox], conf_thr: float, cam_id: int, t: float) -> list[dt.Detection]:
    """Drop low-confidence boxes and wrap as detections."""
    raise NotImplementedError("TODO: M2 PERSON DETECT step 3 — filter_confidence")
