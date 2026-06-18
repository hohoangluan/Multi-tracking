# M11 METRICS

- **Input:** Predictions + ground truth
- **Output:** Metric dicts
- **Param:** mAP / recall / IDF1 / HOTA / Rank-K / Fβ / FP·h⁻¹

## Steps (step-by-step)

1. [`step1_detector.py`](./step1_detector.py) — `detector_metrics()` — Detector: mAP@0.5, recall.
2. [`step2_reid.py`](./step2_reid.py) — `reid_metrics()` — ReID retrieval: mAP, Rank-1/5/K.
3. [`step3_singlecam_track.py`](./step3_singlecam_track.py) — `singlecam_track_metrics()` — Single-cam track: IDF1, HOTA.
4. [`step4_crosscam.py`](./step4_crosscam.py) — `crosscam_metrics()` — Cross-cam MTMC: IDF1.
5. [`step5_realtime_alert.py`](./step5_realtime_alert.py) — `realtime_alert_metrics()` — Realtime alert: P, R, F1.5, absolute FP/hour.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
