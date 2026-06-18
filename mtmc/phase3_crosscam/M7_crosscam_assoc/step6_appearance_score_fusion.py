"""M7 CROSS-CAMERA ASSOCIATION — Step 6/6: Fuse appearance + physics + color + temporal scores.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def appearance_score_fusion(query: dt.ManagedTracklet, candidates: list[dt.Candidate], weights: dict) -> list[dt.Candidate]:
    """Fuse appearance + physics + color + temporal scores."""
    raise NotImplementedError("TODO: M7 CROSS-CAMERA ASSOCIATION step 6 — appearance_score_fusion")
