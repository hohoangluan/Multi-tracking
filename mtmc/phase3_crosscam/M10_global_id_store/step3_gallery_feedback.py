"""M10 GLOBAL ID STORE — Step 3/3: Provide the gallery pool feedback loop back to M7.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def get_gallery_pool(p: cfg.RealtimeParams) -> list[dt.ManagedTracklet]:
    """Provide the gallery pool feedback loop back to M7."""
    raise NotImplementedError("TODO: M10 GLOBAL ID STORE step 3 — get_gallery_pool")
