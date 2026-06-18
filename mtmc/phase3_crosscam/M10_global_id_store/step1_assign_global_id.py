"""M10 GLOBAL ID STORE — Step 1/3: Assign or reuse a global ID for the tracklet.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def assign_global_id(managed: dt.ManagedTracklet, decision: str) -> dt.GlobalIDRecord:
    """Assign or reuse a global ID for the tracklet."""
    raise NotImplementedError("TODO: M10 GLOBAL ID STORE step 1 — assign_global_id")
