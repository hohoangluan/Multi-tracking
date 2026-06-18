"""M1 CALIBRATE / UNDISTORT — Step 1/3: Load intrinsics K, distortion D and homography H.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def load_calibration(path: str) -> dict:
    """Load intrinsics K, distortion D and homography H."""
    raise NotImplementedError("TODO: M1 CALIBRATE / UNDISTORT step 1 — load_calibration")
