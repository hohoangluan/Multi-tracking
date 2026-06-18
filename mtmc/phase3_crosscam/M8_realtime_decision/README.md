# M8 REALTIME DECISION

- **Input:** Matching score + margin (from M7 realtime)
- **Output:** Auto link / alert human / defer
- **Param:** F1.5 tuned, N_frame=5, precision ≥ 50%

## Steps (step-by-step)

1. [`step1_tier1_auto.py`](./step1_tier1_auto.py) — `tier1_auto_link()` — Tier 1: top1≥τ_auto and margin≥m_hi → auto-link to M10.
2. [`step2_tier2_alert.py`](./step2_tier2_alert.py) — `tier2_alert_human()` — Tier 2: top1≥τ_alert → raise a human-review alert.
3. [`step3_tier3_defer.py`](./step3_tier3_defer.py) — `tier3_defer_offline()` — Tier 3: otherwise defer to offline retrieval (M9).

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
