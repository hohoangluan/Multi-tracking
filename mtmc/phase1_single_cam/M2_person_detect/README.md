# M2 PERSON DETECT

- **Input:** Flat image (from M1 Path A)
- **Output:** bbox + confidence
- **Param:** rt(m,1280,0.35) / off(x,1536,0.20,TTA), nms_iou=0.6

## Steps (step-by-step)

1. [`step1_yolo_forward.py`](./step1_yolo_forward.py) — `yolo_forward()` — Run the YOLO forward pass on the frame.
2. [`step2_nms.py`](./step2_nms.py) — `non_max_suppression()` — Suppress overlapping boxes via NMS.
3. [`step3_confidence_filter.py`](./step3_confidence_filter.py) — `filter_confidence()` — Drop low-confidence boxes and wrap as detections.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
