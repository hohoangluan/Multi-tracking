"""M5 ReID FEATURE EXTRACT — Step 3/3: Pool the multi-crop features into one tracklet embedding.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def aggregate_feature(feats: list[dt.FeatureVector]) -> dt.FeatureVector:
    """Pool the multi-crop features into one tracklet embedding."""
    raise NotImplementedError("TODO: M5 ReID FEATURE EXTRACT step 3 — aggregate_feature")
