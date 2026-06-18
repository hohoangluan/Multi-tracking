"""M7 CROSS-CAMERA ASSOCIATION — Step 5/6: Route: 0→new/exited, 1→direct link, ≥2→appearance fusion.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def route_by_candidate_count(candidates: list[dt.Candidate]) -> str:
    """Route: 0→new/exited, 1→direct link, ≥2→appearance fusion."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 5 — route_by_candidate_count")
