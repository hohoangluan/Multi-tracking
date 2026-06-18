"""M9 OFFLINE RETRIEVAL — Step 1/6: Filter the gallery with a loose Δt constraint.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def gallery_filter(query: dt.ManagedTracklet, gallery: list[dt.ManagedTracklet], p: cfg.OfflineParams) -> list[dt.ManagedTracklet]:
    """Filter the gallery with a loose Δt constraint."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 1 — gallery_filter")
