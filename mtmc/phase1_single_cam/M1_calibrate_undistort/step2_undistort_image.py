"""M1 CALIBRATE / UNDISTORT — Step 2/3: Path A: undistort the fisheye frame into a flat image.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def undistort(frame: dt.Frame, K: Any, D: Any) -> dt.Frame:
    """Path A: undistort the fisheye frame into a flat image."""
    raise NotImplementedError("TODO: M1 CALIBRATE / UNDISTORT step 2 — undistort")
