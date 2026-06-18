"""M3 SINGLE-CAM TRACK — Step 1/4: Map the detection foot point to world coordinates.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def foot_to_world(det: dt.Detection, H: Any) -> dt.WorldCoord:
    """Map the detection foot point to world coordinates."""
    raise NotImplementedError("TODO: M3 SINGLE-CAM TRACK step 1 — foot_to_world")
