# M10 GLOBAL ID STORE

- **Input:** Confirmed link/new tracklets (from M8, M9)
- **Output:** Gallery pool
- **Param:** T_forget=120s (rt) / archive ∞ (off)

## Steps (step-by-step)

1. [`step1_assign_global_id.py`](./step1_assign_global_id.py) — `assign_global_id()` — Assign or reuse a global ID for the tracklet.
2. [`step2_store_history.py`](./step2_store_history.py) — `store_history()` — Persist the global ID and its tracking history.
3. [`step3_gallery_feedback.py`](./step3_gallery_feedback.py) — `get_gallery_pool()` — Provide the gallery pool feedback loop back to M7.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
