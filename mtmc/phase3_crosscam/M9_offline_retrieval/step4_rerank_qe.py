"""M9 OFFLINE RETRIEVAL — Step 4/6: Re-rank with k-reciprocal + query expansion.

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def rerank_kreciprocal_qe(candidates: list[dt.Candidate]) -> list[dt.Candidate]:
    """Re-rank with k-reciprocal + query expansion."""
    raise NotImplementedError("TODO: M9 OFFLINE RETRIEVAL step 4 — rerank_kreciprocal_qe")
