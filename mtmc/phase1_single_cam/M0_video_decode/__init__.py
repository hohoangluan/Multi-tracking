"""M0 VIDEO DECODE — re-exports each step's entry function."""

from .step1_ingestion_hwdecode import ingest_and_decode
from .step2_roi_resize import select_roi_and_resize
from .step3_motion_scoring import score_motion
from .step4_sliding_window import sliding_window_select
from .step5_tensor_norm import normalize_to_tensor

__all__ = [
    "ingest_and_decode",
    "select_roi_and_resize",
    "score_motion",
    "sliding_window_select",
    "normalize_to_tensor",
]
