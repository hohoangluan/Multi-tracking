"""M9 OFFLINE RETRIEVAL — Step 6/6: Large margin → auto-accept, else human review → M10.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def decide_by_margin(candidates: list[dt.Candidate]) -> dt.GlobalIDRecord:
    """Large margin → auto-accept, else human review → M10."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 6 — decide_by_margin")
