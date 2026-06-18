"""M11 METRICS — Step 1/5: Detector: mAP@0.5, recall.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def detector_metrics(preds: Any, gts: Any) -> dict:
    """Detector: mAP@0.5, recall."""
    raise NotImplementedError("TODO: M11 METRICS step 1 — detector_metrics")
