"""M5 ReID FEATURE EXTRACT — Step 1/3: Resize/normalize crops into ReID model input tensors.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def preprocess_crops(crops: list[dt.Crop]) -> list[dt.NDArray]:
    """Resize/normalize crops into ReID model input tensors."""
    raise NotImplementedError("TODO: M5 ReID FEATURE EXTRACT step 1 — preprocess_crops")
