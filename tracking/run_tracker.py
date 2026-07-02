"""
M3 — Person tracking (ByteTrack via ultralytics) + CVAT export.

See docs/superpowers/specs/2026-07-02-bytetrack-cvat-annotation-design.md for the full
design, and Task 2 of docs/superpowers/plans/2026-07-02-bytetrack-cvat-annotation-plan.md
for how ultralytics' BYTETracker works internally (Kalman predict, 2-phase IoU matching,
Hungarian assignment) before reading the `model.track()` call below.
"""

from __future__ import annotations


def accumulate_track_history(
    history: dict[int, list[tuple[int, float, float, float, float]]],
    frame_idx: int,
    boxes_xyxy: list[tuple[float, float, float, float]],
    track_ids: list[int],
) -> None:
    """Append (frame_idx, x1, y1, x2, y2) to history[track_id] for each detected track.

    Tracks absent from this frame's boxes_xyxy/track_ids are left untouched — it is the
    caller's job to decide what "absent" means (occluded vs. deleted); this function only
    records what ultralytics reported for this frame.
    """
    for track_id, (x1, y1, x2, y2) in zip(track_ids, boxes_xyxy):
        history.setdefault(track_id, []).append((frame_idx, x1, y1, x2, y2))