# M1 CALIBRATE / UNDISTORT

- **Input:** Distorted frame (fisheye) + K, D, H params
- **Output:** Flat (rectilinear) image + world coord (X,Y) in metres
- **Param:** reprojection error < 0.3m, one shared world origin for 3 cams

## Steps (step-by-step)

1. [`step1_load_calibration.py`](./step1_load_calibration.py) — `load_calibration()` — Load intrinsics K, distortion D and homography H.
2. [`step2_undistort_image.py`](./step2_undistort_image.py) — `undistort()` — Path A: undistort the fisheye frame into a flat image.
3. [`step3_world_projection.py`](./step3_world_projection.py) — `project_to_world()` — Path B: project the foot pixel to world (X,Y) via homography.

> See [pipeline_detail.md](../../../pipeline_detail.md) for the source spec.
