"""M3 SINGLE-CAM TRACK — Step 3/4: Match detections to tracks (world dist + IoU + ReID-on-occlusion).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def hungarian_match(tracks: list[dt.Tracklet], dets: list[dt.Detection], p: cfg.RealtimeParams) -> list[tuple[int, int]]:
    """Match detections to tracks (world dist + IoU + ReID-on-occlusion)."""
    raise NotImplementedError("TODO: M3 SINGLE-CAM TRACK step 3 — hungarian_match")
