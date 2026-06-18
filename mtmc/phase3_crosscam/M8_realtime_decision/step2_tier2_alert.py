"""M8 REALTIME DECISION — Step 2/3: Tier 2: top1≥τ_alert → raise a human-review alert.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def tier2_alert_human(score: dt.MatchScore, p: cfg.RealtimeParams) -> bool:
    """Tier 2: top1≥τ_alert → raise a human-review alert."""
    raise NotImplementedError("TODO: M8 REALTIME DECISION step 2 — tier2_alert_human")
