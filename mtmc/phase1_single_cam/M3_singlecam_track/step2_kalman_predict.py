"""M3 SINGLE-CAM TRACK — Step 2/4: Predict the next world-space state (X,Y,vX,vY).

See the module README.md and pipeline_detail.md for the full I/O contract.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional

from mtmc.common import datatypes as dt
from mtmc.config import params as cfg


def kalman_predict(track: dt.Tracklet) -> dt.KalmanState:
    """Predict the next world-space state (X,Y,vX,vY)."""
    raise NotImplementedError("TODO: M3 SINGLE-CAM TRACK step 2 — kalman_predict")
