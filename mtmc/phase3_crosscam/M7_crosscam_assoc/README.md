# M7 CROSS-CAMERA ASSOCIATION

- **Input:** Query tracklet (completed) + gallery pool (from M10)
- **Output:** Candidate list + scores → M8 or M9
- **Param:** fusion: α·cos(feat)+β·phys_penalty+γ·color+δ·temporal

## Steps (step-by-step)

1. [`step1_fov_overlap_check.py`](./step1_fov_overlap_check.py) — `has_fov_overlap()` — Check whether two cameras' fields of view overlap.
2. [`step2_geometry_world_match.py`](./step2_geometry_world_match.py) — `geometry_world_match()` — Overlap case: match directly on world coordinates (AUTO).
3. [`step3_extrapolate_physics.py`](./step3_extrapolate_physics.py) — `extrapolate_physics()` — Non-overlap case: extrapolate exit position/velocity/heading/time.
4. [`step4_physical_constraints_filter.py`](./step4_physical_constraints_filter.py) — `physical_constraints_filter()` — Filter by topology, Δt∈[d/v_max, d/v_min], zone, |Δv|.
5. [`step5_candidate_routing.py`](./step5_candidate_routing.py) — `route_by_candidate_count()` — Route: 0→new/exited, 1→direct link, ≥2→appearance fusion.
6. [`step6_appearance_score_fusion.py`](./step6_appearance_score_fusion.py) — `appearance_score_fusion()` — Fuse appearance + physics + color + temporal scores.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
