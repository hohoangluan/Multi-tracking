"""M1 CALIBRATE / UNDISTORT — Step 3/3: Path B: project the foot pixel to world (X,Y) via homography.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def project_to_world(foot: dt.FootPoint, H: Any) -> dt.WorldCoord:
    """Path B: project the foot pixel to world (X,Y) via homography."""
    raise NotImplementedError("TODO: M1 CALIBRATE / UNDISTORT step 3 — project_to_world")
