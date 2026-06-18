"""M8 REALTIME DECISION — Step 1/3: Tier 1: top1≥τ_auto and margin≥m_hi → auto-link to M10.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def tier1_auto_link(score: dt.MatchScore, p: cfg.RealtimeParams) -> Optional[dt.GlobalIDRecord]:
    """Tier 1: top1≥τ_auto and margin≥m_hi → auto-link to M10."""
    raise NotImplementedError("TODO: M8 REALTIME DECISION step 1 — tier1_auto_link")
