"""M3 SINGLE-CAM TRACK — Step 4/4: Update matched, age/delete missed, init new tracks.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def update_lifecycle(tracks: list[dt.Tracklet], dets: list[dt.Detection], matches: list[tuple[int, int]], p: cfg.RealtimeParams) -> list[dt.Tracklet]:
    """Update matched, age/delete missed, init new tracks."""
    raise NotImplementedError("TODO: M3 SINGLE-CAM TRACK step 4 — update_lifecycle")
