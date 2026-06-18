# M5 ReID FEATURE EXTRACT

- **Input:** Top-K crops
- **Output:** Feature vector
- **Param:** rt: OSNet / off: ensemble + rerank

## Steps (step-by-step)

1. [`step1_preprocess_crops.py`](./step1_preprocess_crops.py) — `preprocess_crops()` — Resize/normalize crops into ReID model input tensors.
2. [`step2_extract_features.py`](./step2_extract_features.py) — `extract_features()` — Run the ReID model (OSNet realtime / ensemble offline).
3. [`step3_aggregate.py`](./step3_aggregate.py) — `aggregate_feature()` — Pool the multi-crop features into one tracklet embedding.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
