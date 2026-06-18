# M4 QUALITY GATE

- **Input:** Tracklet + crops
- **Output:** Top-K best crops
- **Param:** Hmin=96px, K=5 (rt) / 5–8 (off)

## Steps (step-by-step)

1. [`step1_filter_quality.py`](./step1_filter_quality.py) — `filter_quality()` — Drop crops that are too small / blurry / occluded / blown-out.
2. [`step2_select_topk.py`](./step2_select_topk.py) — `select_topk()` — Keep only the K best crops by quality score.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
