"""M7 CROSS-CAMERA ASSOCIATION — Step 3/6: Non-overlap case: extrapolate exit position/velocity/heading/time.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def extrapolate_physics(query: dt.ManagedTracklet) -> dt.WorldCoord:
    """Non-overlap case: extrapolate exit position/velocity/heading/time."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 3 — extrapolate_physics")
