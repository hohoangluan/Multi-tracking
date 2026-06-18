"""M11 METRICS — Step 5/5: Realtime alert: P, R, F1.5, absolute FP/hour.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def realtime_alert_metrics(preds: Any, gts: Any) -> dict:
    """Realtime alert: P, R, F1.5, absolute FP/hour."""
    raise NotImplementedError("TODO: M11 METRICS step 5 — realtime_alert_metrics")
