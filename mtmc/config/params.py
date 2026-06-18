"""Pipeline parameters for the two operating modes.

Values mirror the "Bảng tham số khởi điểm" table in pipeline_detail.md.
Thresholds left at 0.0 are F1.5-tuned and must be calibrated on data (TODO).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RealtimeParams:
    """Fast path — lighter models, tight time gating, high precision."""

    # M0 — video decode
    target_fps: int = 15
    decode: str = "NVDEC"
    ring_size: int = 64

    # M2 — person detect
    detector: str = "yolov8m"
    det_imgsz: int = 1280
    det_conf: float = 0.35
    nms_iou: float = 0.6

    # M3 — single-cam track
    max_age: int = 60

    # M4 — quality gate
    crop_hmin: int = 96
    crop_topk: int = 5

    # M5 — ReID
    reid_model: str = "osnet"

    # M7 — cross-cam time gating
    dt_mode: str = "tight"

    # M8 — tiered decision thresholds (F1.5-tuned, TODO calibrate)
    tau_auto: float = 0.0
    margin_hi: float = 0.0
    tau_alert: float = 0.0
    n_frame: int = 5

    # M10 — gallery retention
    forget_seconds: float = 120.0


@dataclass
class OfflineParams:
    """Exhaustive path — heavy ensemble, loose gating, recall-first."""

    # M2 — person detect
    detector: str = "yolov8x"
    det_imgsz: int = 1536
    det_conf: float = 0.20
    tta: bool = True
    nms_iou: float = 0.6

    # M3 — single-cam track
    max_age: int = 60

    # M4 — quality gate
    crop_hmin: int = 96
    crop_topk: int = 8

    # M5 — ReID
    reid_model: str = "ensemble"

    # M7 — cross-cam time gating
    dt_mode: str = "loose"

    # M9 — retrieval
    rerank: bool = True

    # M10 — gallery retention (archive forever)
    forget_seconds: float = float("inf")
