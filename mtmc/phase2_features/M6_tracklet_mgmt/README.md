# M6 TRACKLET MANAGEMENT

- **Input:** Feature vector + tracklets from M3
- **Output:** tracklet + meta + feat (ManagedTracklet)
- **Param:** stitch intra-camera breaks; attach entry/exit/heading/velocity

## Steps (step-by-step)

1. [`step1_lifecycle.py`](./step1_lifecycle.py) — `manage_lifecycle()` — Manage the tracklet lifecycle (active / completed).
2. [`step2_stitch_intracam.py`](./step2_stitch_intracam.py) — `stitch_intracam()` — Stitch broken tracklet fragments within the same camera.
3. [`step3_attach_metadata.py`](./step3_attach_metadata.py) — `attach_metadata()` — Attach metadata (heading, velocity, entry/exit zone) + feature.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
