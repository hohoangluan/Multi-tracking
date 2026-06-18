"""M9 OFFLINE RETRIEVAL — Step 5/6: Choose Top-K adaptively to optimize the result.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def adaptive_topk(candidates: list[dt.Candidate]) -> list[dt.Candidate]:
    """Choose Top-K adaptively to optimize the result."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 5 — adaptive_topk")
