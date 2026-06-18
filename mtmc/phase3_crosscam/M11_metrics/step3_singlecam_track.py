"""M11 METRICS — Step 3/5: Single-cam track: IDF1, HOTA.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def singlecam_track_metrics(preds: Any, gts: Any) -> dict:
    """Single-cam track: IDF1, HOTA."""
    raise NotImplementedError("TODO: M11 METRICS step 3 — singlecam_track_metrics")
