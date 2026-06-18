# M9 OFFLINE RETRIEVAL

- **Input:** Deferred tracklets from realtime + M7 offline
- **Output:** Global ID assignment
- **Param:** exhaustive search, target Rank-K recall ≥ 99%

## Steps (step-by-step)

1. [`step1_gallery_filter.py`](./step1_gallery_filter.py) — `gallery_filter()` — Filter the gallery with a loose Δt constraint.
2. [`step2_multishot_match.py`](./step2_multishot_match.py) — `multishot_match()` — Match across multiple crops per identity.
3. [`step3_fuse_scores.py`](./step3_fuse_scores.py) — `fuse_scores()` — Fuse OSNet + ViT + color + shape scores.
4. [`step4_rerank_qe.py`](./step4_rerank_qe.py) — `rerank_kreciprocal_qe()` — Re-rank with k-reciprocal + query expansion.
5. [`step5_adaptive_topk.py`](./step5_adaptive_topk.py) — `adaptive_topk()` — Choose Top-K adaptively to optimize the result.
6. [`step6_decision_margin.py`](./step6_decision_margin.py) — `decide_by_margin()` — Large margin → auto-accept, else human review → M10.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
