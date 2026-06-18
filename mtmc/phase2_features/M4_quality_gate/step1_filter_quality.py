"""M4 QUALITY GATE — Step 1/2: Drop crops that are too small / blurry / occluded / blown-out.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def filter_quality(crops: list[dt.Crop], p: cfg.RealtimeParams) -> list[dt.Crop]:
    """Drop crops that are too small / blurry / occluded / blown-out."""
    raise NotImplementedError("TODO: M4 QUALITY GATE step 1 — filter_quality")
