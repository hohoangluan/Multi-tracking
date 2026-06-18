"""M6 TRACKLET MANAGEMENT — Step 3/3: Attach metadata (heading, velocity, entry/exit zone) + feature.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def attach_metadata(tracklet: dt.Tracklet, feat: dt.FeatureVector) -> dt.ManagedTracklet:
    """Attach metadata (heading, velocity, entry/exit zone) + feature."""
    raise NotImplementedError("TODO: M6 TRACKLET MANAGEMENT step 3 — attach_metadata")
