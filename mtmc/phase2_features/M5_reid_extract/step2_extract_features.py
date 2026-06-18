"""M5 ReID FEATURE EXTRACT — Step 2/3: Run the ReID model (OSNet realtime / ensemble offline).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def extract_features(tensors: list[dt.NDArray], mode: dt.Mode) -> list[dt.FeatureVector]:
    """Run the ReID model (OSNet realtime / ensemble offline)."""
    raise NotImplementedError("TODO: M5 ReID FEATURE EXTRACT step 2 — extract_features")
