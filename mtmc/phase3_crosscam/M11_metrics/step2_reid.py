"""M11 METRICS — Step 2/5: ReID retrieval: mAP, Rank-1/5/K.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def reid_metrics(preds: Any, gts: Any) -> dict:
    """ReID retrieval: mAP, Rank-1/5/K."""
    raise NotImplementedError("TODO: M11 METRICS step 2 — reid_metrics")
