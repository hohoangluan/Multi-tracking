"""M9 OFFLINE RETRIEVAL — Step 3/6: Fuse OSNet + ViT + color + shape scores.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def fuse_scores(candidates: list[dt.Candidate]) -> list[dt.Candidate]:
    """Fuse OSNet + ViT + color + shape scores."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 3 — fuse_scores")
