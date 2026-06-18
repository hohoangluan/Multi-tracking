"""M6 TRACKLET MANAGEMENT — Step 1/3: Manage the tracklet lifecycle (active / completed).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def manage_lifecycle(tracklets: list[dt.Tracklet]) -> list[dt.Tracklet]:
    """Manage the tracklet lifecycle (active / completed)."""
    raise NotImplementedError("TODO: M6 TRACKLET MANAGEMENT step 1 — manage_lifecycle")
