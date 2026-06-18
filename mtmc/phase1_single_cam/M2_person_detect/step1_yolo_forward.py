"""M2 PERSON DETECT — Step 1/3: Run the YOLO forward pass on the frame.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def yolo_forward(image: dt.NDArray, p: cfg.RealtimeParams) -> list[dt.BBox]:
    """Run the YOLO forward pass on the frame."""
    raise NotImplementedError("TODO: M2 PERSON DETECT step 1 — yolo_forward")
