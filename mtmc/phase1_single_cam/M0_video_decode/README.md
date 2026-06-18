# M0 VIDEO DECODE

- **Input:** RTSP stream / mp4 (2880×1620, 25–40 FPS)
- **Output:** AI tensor (15fps), BGR
- **Param:** target_fps=15, decode=NVDEC, ring_size=64

## Steps (step-by-step)

1. [`step1_ingestion_hwdecode.py`](./step1_ingestion_hwdecode.py) — `ingest_and_decode()` — Connect to the stream and HW-decode (NVDEC) frames in real time.
2. [`step2_roi_resize.py`](./step2_roi_resize.py) — `select_roi_and_resize()` — Crop the region of interest and resize to the AI input size.
3. [`step3_motion_scoring.py`](./step3_motion_scoring.py) — `score_motion()` — Score how much changed vs the previous frame.
4. [`step4_sliding_window.py`](./step4_sliding_window.py) — `sliding_window_select()` — Pick the best 15 frames per second from the buffer.
5. [`step5_tensor_norm.py`](./step5_tensor_norm.py) — `normalize_to_tensor()` — Normalize the image matrix into an AI-ready tensor.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
