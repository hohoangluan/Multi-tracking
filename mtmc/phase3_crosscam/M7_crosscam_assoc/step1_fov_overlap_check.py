"""M7 CROSS-CAMERA ASSOCIATION — Step 1/6: Check whether two cameras' fields of view overlap.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def has_fov_overlap(cam_a: int, cam_b: int) -> bool:
    """Check whether two cameras' fields of view overlap."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 1 — has_fov_overlap")
