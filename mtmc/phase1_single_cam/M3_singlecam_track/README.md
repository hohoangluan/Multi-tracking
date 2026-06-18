# M3 SINGLE-CAM TRACK

- **Input:** Detections @ frame t + world coord (from M1 Path B)
- **Output:** Active tracklets in world space
- **Param:** Kalman in world space (m, m/s); delete if miss > 60 frames

## Steps (step-by-step)

1. [`step1_foot_to_world.py`](./step1_foot_to_world.py) — `foot_to_world()` — Map the detection foot point to world coordinates.
2. [`step2_kalman_predict.py`](./step2_kalman_predict.py) — `kalman_predict()` — Predict the next world-space state (X,Y,vX,vY).
3. [`step3_hungarian_match.py`](./step3_hungarian_match.py) — `hungarian_match()` — Match detections to tracks (world dist + IoU + ReID-on-occlusion).
4. [`step4_track_lifecycle.py`](./step4_track_lifecycle.py) — `update_lifecycle()` — Update matched, age/delete missed, init new tracks.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
