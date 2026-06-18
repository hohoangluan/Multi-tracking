"""M7 CROSS-CAMERA ASSOCIATION — Step 4/6: Filter by topology, Δt∈[d/v_max, d/v_min], zone, |Δv|.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def physical_constraints_filter(query: dt.ManagedTracklet, gallery: list[dt.ManagedTracklet], p: cfg.RealtimeParams) -> list[dt.Candidate]:
    """Filter by topology, Δt∈[d/v_max, d/v_min], zone, |Δv|."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 4 — physical_constraints_filter")
