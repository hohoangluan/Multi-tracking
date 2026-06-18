"""M7 CROSS-CAMERA ASSOCIATION — Step 2/6: Overlap case: match directly on world coordinates (AUTO).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def geometry_world_match(query: dt.ManagedTracklet, gallery: list[dt.ManagedTracklet]) -> list[dt.Candidate]:
    """Overlap case: match directly on world coordinates (AUTO)."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 2 — geometry_world_match")
