"""M0 VIDEO DECODE — Step 1/5: Connect to the stream and HW-decode (NVDEC) frames in real time.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def ingest_and_decode(source: str, p: cfg.RealtimeParams) -> Iterator[dt.Frame]:
    """Connect to the stream and HW-decode (NVDEC) frames in real time."""
    raise NotImplementedError("TODO: M0 VIDEO DECODE step 1 — ingest_and_decode")
