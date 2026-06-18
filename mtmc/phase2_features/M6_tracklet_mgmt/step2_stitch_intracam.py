"""M6 TRACKLET MANAGEMENT — Step 2/3: Stitch broken tracklet fragments within the same camera.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def stitch_intracam(tracklets: list[dt.Tracklet]) -> list[dt.Tracklet]:
    """Stitch broken tracklet fragments within the same camera."""
    raise NotImplementedError("TODO: M6 TRACKLET MANAGEMENT step 2 — stitch_intracam")
