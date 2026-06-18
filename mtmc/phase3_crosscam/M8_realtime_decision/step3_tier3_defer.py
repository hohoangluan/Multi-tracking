"""M8 REALTIME DECISION — Step 3/3: Tier 3: otherwise defer to offline retrieval (M9).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def tier3_defer_offline(score: dt.MatchScore, p: cfg.RealtimeParams) -> bool:
    """Tier 3: otherwise defer to offline retrieval (M9)."""
    raise NotImplementedError("TODO: M8 REALTIME DECISION step 3 — tier3_defer_offline")
