"""M11 METRICS — Step 4/5: Cross-cam MTMC: IDF1.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def crosscam_metrics(preds: Any, gts: Any) -> dict:
    """Cross-cam MTMC: IDF1."""
    raise NotImplementedError("TODO: M11 METRICS step 4 — crosscam_metrics")
