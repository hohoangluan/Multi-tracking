"""M9 OFFLINE RETRIEVAL — Step 2/6: Match across multiple crops per identity.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def multishot_match(query: dt.ManagedTracklet, gallery: list[dt.ManagedTracklet]) -> list[dt.Candidate]:
    """Match across multiple crops per identity."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 2 — multishot_match")
