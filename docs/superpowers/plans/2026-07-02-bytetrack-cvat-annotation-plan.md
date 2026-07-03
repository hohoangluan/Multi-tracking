# ByteTrack (ultralytics) + CVAT Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task. This plan is a **teaching session run inline with
> the user** — do NOT dispatch to fresh subagents (superpowers:subagent-driven-development
> is explicitly the wrong fit here): a subagent has no memory of the user's questions and
> can't do the live "read this source function, explain it, check understanding" loop
> that Task 2 requires. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tracking/run_tracker.py` + `tracking/cvat_export.py` so a real video in
`dataset/2026-06-10/` goes end-to-end: fisheye-undistort → YOLO detect → ByteTrack
(via `ultralytics` `model.track()`) → CVAT Video 1.1 XML, ready to import and correct in
CVAT.

**Architecture:** Reuse `preprocessing.m0_ingest.M0Decoder` for undistorted frames; feed
each frame individually into `model.track(frame, persist=True, tracker="bytetrack.yaml")`
so ultralytics' `BYTETracker` keeps track state across the call sequence; accumulate
per-track-id bbox history in a plain dict; hand-write the CVAT XML serializer since no
library targets this exact schema.

**Tech Stack:** `ultralytics` (YOLO model + built-in ByteTrack), `opencv-python` (video
I/O, already used by `M0Decoder`), `xml.etree.ElementTree` (stdlib), `unittest` (stdlib —
no `pytest` currently in `requirements.txt`, don't add it for two small test files).

## Global Constraints

- Use `ultralytics` `model.track()` with `tracker="bytetrack.yaml"`. Do NOT hand-roll
  Kalman filter, cost matrix, Hungarian assignment, or 2-phase matching — ultralytics
  already implements this correctly.
- Feed frames to `model.track()` **one at a time** (`frame.data` from `M0Decoder`, not
  `source=video_path`) so the fisheye-undistort step (M0/M1) runs before tracking (M2/M3),
  matching the module order in `pipeline_detail.md`.
- Call `model.track(..., persist=True)` on **every** decoded frame, even ones with zero
  detections — do not skip frames, or the tracker's internal `age`/`track_buffer` counters
  desync from real time.
- CVAT export uses only `xml.etree.ElementTree` (stdlib) — target is Python 3.8
  (`__pycache__/*.cpython-38.pyc` confirms this), so **do not use `ET.indent()`**
  (added in Python 3.9) or any 3.9+-only stdlib API.
- Every track's history must end with an explicit `outside="1"` box on the frame right
  after its last real detection (unless that track is still alive at the final frame) —
  this is CVAT's required "track ends here" marker, not optional styling.
- Out of scope, do not implement: ReID/BoT-SORT (`with_reid`), calibration/world-space
  projection, multi-camera association, tuning `bytetrack.yaml` thresholds. If tempted to
  add any of these "while we're in there," don't — flag it as a follow-up instead.
- Test video source: a real file under `dataset/2026-06-10/*.mp4`. Do not use
  `frames_test/`.
- Before writing code that calls an `ultralytics` tracker internal, read the actual
  installed source for it first (Task 2) — this is a hard requirement from the user
  ("teach me code, not vibecode"), not a nice-to-have.

---

## Task 1: Package scaffold + dependency

**Files:**
- Create: `tracking/__init__.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces: `tracking` becomes an importable package (`from tracking.cvat_export import ...`,
  `from tracking.run_tracker import ...` in later tasks).

- [ ] **Step 1: Create the package directory and empty `__init__.py`**

```bash
mkdir -p tracking
touch tracking/__init__.py
```

- [ ] **Step 2: Uncomment the tracking dependency in `requirements.txt`**

In `requirements.txt`, change:
```
# ultralytics            # YOLOv8/YOLO11 detector
# torch
# torchvision
```
to:
```
ultralytics              # YOLO detector + built-in ByteTrack/BoT-SORT tracker
torch
torchvision
```
(Leave `scipy`/`filterpy` commented — ultralytics vendors its own `scipy` call for
Hungarian matching internally; we don't call scipy directly.)

- [ ] **Step 3: Verify ultralytics + torch import cleanly and locate the installed package path**

Run: `python3 -c "import ultralytics, os; print(ultralytics.__version__); print(os.path.dirname(ultralytics.__file__))"`
Expected: prints a version (e.g. `8.4.75`) and an absolute path like
`/usr/lib/python3.8/site-packages/ultralytics` (or your venv's site-packages) — **write
this path down**, Task 2 reads files inside it.

- [ ] **Step 4: Commit**

```bash
git add tracking/__init__.py requirements.txt
git commit -m "Scaffold tracking package, enable ultralytics dependency"
```

---

## Task 2: Read the ultralytics ByteTrack source before using it

**Files:** none created/modified — this task is reading + a written checkpoint, not code.

**Interfaces:** none (produces understanding, not a function).

This task exists because the whole point of this session is understanding what
`model.track()` does, not just calling it. Use the path found in Task 1 Step 3
(call it `$ULTRA`) to open these files with the Read tool, in this order:

- [ ] **Step 1: Read the tracker config — `$ULTRA/cfg/trackers/bytetrack.yaml`**

Find and note the default value of each of these fields (they gate every decision
BYTETracker makes):
  - `track_high_thresh` — confidence above which a detection is "high-confidence" (used
    in the first matching pass).
  - `track_low_thresh` — confidence floor; detections below this are discarded entirely.
  - `new_track_thresh` — confidence above which an *unmatched* detection is allowed to
    start a brand-new track (prevents spawning tracks from noisy low-conf boxes).
  - `track_buffer` — how many frames a track survives with zero matches before deletion
    (this is the `max_age` equivalent from the old hand-rolled design).
  - `match_thresh` — IoU/cost threshold above which a match is rejected even if it's the
    best available pairing.

- [ ] **Step 2: Read `$ULTRA/trackers/byte_tracker.py` — the `BYTETracker.update()` method**

Trace through it and confirm (write down where each happens, by function name):
  1. Every existing track calls `predict()` (Kalman prediction) **before** any matching
     happens — this is why the tracker handles motion between frames instead of assuming
     "last known bbox = current bbox."
  2. Detections are split into "high confidence" and "low confidence" groups using
     `track_high_thresh`/`track_low_thresh` from the yaml.
  3. **First association pass:** high-confidence detections are matched against ALL
     existing tracks (both currently-tracked and recently-lost) via IoU cost.
  4. **Second association pass:** tracks that didn't get matched in pass 1 are matched
     against the *low-confidence* detections — this is ByteTrack's core idea: a track
     surviving one frame of "I only see a blurry/occluded partial box" is better than
     losing the ID and creating a new one.
  5. Tracks unmatched in both passes get `mark_lost()`; detections unmatched in both
     passes above `new_track_thresh` spawn new tracks.

- [ ] **Step 3: Read `$ULTRA/trackers/utils/matching.py`**

Confirm:
  - `iou_distance(tracks, detections)` builds the cost matrix as `1 - IoU` (so lower
    cost = better match, matching the convention `linear_sum_assignment` expects).
  - `linear_assignment(cost_matrix, thresh)` calls `scipy.optimize.linear_sum_assignment`
    (true Hungarian algorithm — optimal assignment, not greedy) if `scipy`/`lap` is
    available, then throws out any pair whose cost exceeds `thresh`.

- [ ] **Step 4: Read `$ULTRA/trackers/utils/kalman_filter.py`**

Confirm the state vector tracked per object is 8-dimensional: `(x, y, aspect_ratio,
height, vx, vy, v_aspect, v_height)` — position + size + their velocities, constant
velocity model. `predict()` advances the state one frame using the velocity terms;
`update()` corrects it toward the matched detection's actual box (standard Kalman gain
blend).

- [ ] **Step 5: Write a comprehension checkpoint**

In your own words (a few sentences, spoken or typed to whoever is guiding this session —
no file output required for this step), answer: **"Why does ByteTrack's 2-phase matching
survive brief occlusion better than matching once against all detections?"** The correct
shape of the answer: a temporarily-occluded person still produces a low-confidence
detection (partial box) most frames; phase 2 gives already-established tracks first claim
on those low-confidence boxes instead of discarding them, so the same `track_id` re-attaches
instead of the track dying and a new ID being born when the person re-emerges clearly.
If your answer doesn't match this shape, re-read Step 2 before moving on — Task 5's
`--preview-video` output is where you'll see this behavior (or its absence) for real.

- [ ] **Step 6: Commit the checkpoint (no code changes, but records the session moved past this gate)**

```bash
git commit --allow-empty -m "Checkpoint: read and understand ultralytics ByteTrack internals before use"
```

---

## Task 3: CVAT XML exporter

**Files:**
- Create: `tracking/cvat_export.py`
- Test: `tests/test_cvat_export.py`

**Interfaces:**
- Produces: `boxes_to_cvat_xml(history: dict[int, list[tuple[int, float, float, float, float]]], total_frames: int, out_path: str | Path, label: str = "person") -> None`
  where each tuple is `(frame_idx, x1, y1, x2, y2)`. Task 4/5 build `history` and pass it
  here unchanged.

- [ ] **Step 1: Create the tests directory and write the failing test**

```bash
mkdir -p tests
touch tests/__init__.py
```

Create `tests/test_cvat_export.py`:

```python
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from tracking.cvat_export import boxes_to_cvat_xml


class TestBoxesToCvatXml(unittest.TestCase):
    def test_two_tracks_one_disappears_early(self):
        # Track 1: present frames 0,1,2 (visible to the end of the clip, 3 frames total).
        # Track 2: present frames 0,1 only (disappears before the clip ends).
        history = {
            1: [(0, 10.0, 10.0, 50.0, 90.0), (1, 12.0, 10.0, 52.0, 90.0), (2, 14.0, 10.0, 54.0, 90.0)],
            2: [(0, 200.0, 20.0, 240.0, 100.0), (1, 202.0, 20.0, 242.0, 100.0)],
        }
        with TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "annotations.xml"
            boxes_to_cvat_xml(history, total_frames=3, out_path=out_path, label="person")

            tree = ET.parse(out_path)
            root = tree.getroot()

            self.assertEqual(root.find("version").text, "1.1")
            tracks = root.findall("track")
            self.assertEqual(len(tracks), 2)

            track_by_id = {t.get("id"): t for t in tracks}
            self.assertEqual(track_by_id["1"].get("label"), "person")

            # Track 1 stayed alive through the last frame (2) of a 3-frame clip -> no
            # outside=1 terminator needed.
            boxes_t1 = track_by_id["1"].findall("box")
            self.assertEqual(len(boxes_t1), 3)
            self.assertEqual(boxes_t1[-1].get("outside"), "0")

            # Track 2 disappeared after frame 1 (clip has frames 0,1,2) -> must get an
            # outside=1 terminator box on frame 2.
            boxes_t2 = track_by_id["2"].findall("box")
            self.assertEqual(len(boxes_t2), 3)
            self.assertEqual(boxes_t2[0].get("outside"), "0")
            self.assertEqual(boxes_t2[1].get("outside"), "0")
            self.assertEqual(boxes_t2[2].get("frame"), "2")
            self.assertEqual(boxes_t2[2].get("outside"), "1")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_cvat_export -v`
Expected: `ModuleNotFoundError: No module named 'tracking.cvat_export'` (or `ImportError`) —
the file doesn't exist yet.

- [ ] **Step 3: Write the implementation**

Create `tracking/cvat_export.py`:

```python
"""
CVAT Video 1.1 XML exporter.

Format reference (schema CVAT expects for a video annotation task import):

    <annotations>
      <version>1.1</version>
      <track id="1" label="person">
        <box frame="0" xtl="10.00" ytl="10.00" xbr="50.00" ybr="90.00"
             outside="0" occluded="0" keyframe="1"/>
        ...
        <box frame="42" xtl="0.00" ytl="0.00" xbr="0.00" ybr="0.00"
             outside="1" occluded="0" keyframe="1"/>
      </track>
    </annotations>

`outside="1"` is CVAT's explicit "this track stops existing at this frame" marker —
without it, CVAT interpolates the box forward past where the person actually left the
tracked region. We add exactly one outside=1 box, one frame after a track's last real
detection, unless that track survived to the very last frame of the clip.

Targets Python 3.8: no `ET.indent()` (3.9+) — output is unformatted but valid XML,
which CVAT parses fine.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def boxes_to_cvat_xml(
    history: dict[int, list[tuple[int, float, float, float, float]]],
    total_frames: int,
    out_path: str | Path,
    label: str = "person",
) -> None:
    root = ET.Element("annotations")
    ET.SubElement(root, "version").text = "1.1"

    for track_id in sorted(history):
        frames = sorted(history[track_id], key=lambda f: f[0])
        track_el = ET.SubElement(root, "track", id=str(track_id), label=label)

        for frame_idx, x1, y1, x2, y2 in frames:
            ET.SubElement(
                track_el, "box",
                frame=str(frame_idx),
                xtl=f"{x1:.2f}", ytl=f"{y1:.2f}", xbr=f"{x2:.2f}", ybr=f"{y2:.2f}",
                outside="0", occluded="0", keyframe="1",
            )

        last_frame = frames[-1][0]
        end_frame = last_frame + 1
        if end_frame < total_frames:
            ET.SubElement(
                track_el, "box",
                frame=str(end_frame),
                xtl="0.00", ytl="0.00", xbr="0.00", ybr="0.00",
                outside="1", occluded="0", keyframe="1",
            )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m unittest tests.test_cvat_export -v`
Expected: `OK` (1 test passed).

- [ ] **Step 5: Commit**

```bash
git add tracking/cvat_export.py tests/__init__.py tests/test_cvat_export.py
git commit -m "Add CVAT Video 1.1 XML exporter with outside=1 track termination"
```

---

## Task 4: Track-history accumulator (pure function, testable without a model or video)

**Files:**
- Create: `tracking/run_tracker.py` (this task only adds `accumulate_track_history`; CLI
  wiring is Task 5)
- Test: `tests/test_run_tracker.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `accumulate_track_history(history: dict[int, list[tuple[int, float, float, float, float]]], frame_idx: int, boxes_xyxy: list[tuple[float, float, float, float]], track_ids: list[int]) -> None`
  (mutates `history` in place). Task 5 calls this once per decoded frame with the boxes/ids
  it got back from `model.track()`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_run_tracker.py`:

```python
import unittest

from tracking.run_tracker import accumulate_track_history


class TestAccumulateTrackHistory(unittest.TestCase):
    def test_appends_per_track_across_frames_and_ignores_absent_ids(self):
        history: dict = {}

        # Frame 0: two people, track ids 1 and 2.
        accumulate_track_history(
            history, frame_idx=0,
            boxes_xyxy=[(10.0, 10.0, 50.0, 90.0), (200.0, 20.0, 240.0, 100.0)],
            track_ids=[1, 2],
        )
        # Frame 1: only track 1 detected (track 2 occluded this frame -> caller simply
        # doesn't pass it, it is NOT this function's job to invent a box for it).
        accumulate_track_history(
            history, frame_idx=1,
            boxes_xyxy=[(12.0, 10.0, 52.0, 90.0)],
            track_ids=[1],
        )

        self.assertEqual(
            history[1],
            [(0, 10.0, 10.0, 50.0, 90.0), (1, 12.0, 10.0, 52.0, 90.0)],
        )
        self.assertEqual(history[2], [(0, 200.0, 20.0, 240.0, 100.0)])

    def test_empty_frame_is_a_no_op(self):
        history: dict = {}
        accumulate_track_history(history, frame_idx=0, boxes_xyxy=[], track_ids=[])
        self.assertEqual(history, {})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_run_tracker -v`
Expected: `ModuleNotFoundError: No module named 'tracking.run_tracker'`.

- [ ] **Step 3: Write the minimal implementation**

Create `tracking/run_tracker.py` with just this function for now (CLI/model wiring is
appended in Task 5 — this keeps this task's diff reviewable on its own):

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m unittest tests.test_run_tracker -v`
Expected: `OK` (2 tests passed).

- [ ] **Step 5: Commit**

```bash
git add tracking/run_tracker.py tests/test_run_tracker.py
git commit -m "Add track-history accumulator for tracking.run_tracker"
```

---

## Task 5: CLI wiring — real video through M0Decoder + model.track() + preview + export

**Files:**
- Modify: `tracking/run_tracker.py` (append CLI + `main()` below the Task 4 function)

**Interfaces:**
- Consumes: `preprocessing.m0_ingest.M0Decoder` (existing, `DecodedFrame{data, frame_idx, timestamp_ms, source}`),
  `tracking.run_tracker.accumulate_track_history` (Task 4),
  `tracking.cvat_export.boxes_to_cvat_xml` (Task 3).
- Produces: `python3 -m tracking.run_tracker <video> --output <dir> [...]` CLI entry point.

No unit test here — this task's correctness gate is a real run in Task 6 (it depends on a
GPU/model and a real video, which is exactly what unit tests should avoid depending on).

- [ ] **Step 1: Add imports to the top of `tracking/run_tracker.py`, then append the CLI and `main()` below the existing `accumulate_track_history` function**

Right after the existing `from __future__ import annotations` line at the top of the
file, add:

```python
import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO

from preprocessing.m0_ingest import M0Decoder
from .cvat_export import boxes_to_cvat_xml

PERSON_CLASS = 0
```

Then, below the existing `accumulate_track_history` function, append:

```python
def parse_args():
    p = argparse.ArgumentParser(description="M3 tracker (ByteTrack via ultralytics) -> CVAT export")
    p.add_argument("video", help="Path to source video, e.g. dataset/2026-06-10/00-52-57.mp4")
    p.add_argument("--output", "-o", required=True, help="Output directory for annotations.xml")
    p.add_argument("--model", default="yolo26m.pt", help="Ultralytics weights file (default: yolo26m.pt)")
    p.add_argument("--tracker", default="bytetrack.yaml", help="ultralytics tracker config (default: bytetrack.yaml)")
    p.add_argument("--conf", type=float, default=0.3, help="Detection confidence threshold")
    p.add_argument("--imgsz", type=int, default=960, help="Inference image size")
    p.add_argument("--k1", type=float, default=-0.30, help="Fisheye correction coefficient (see M0Decoder)")
    p.add_argument("--preview-video", default=None, help="If set, write an annotated mp4 here")
    p.add_argument("--max-frames", type=int, default=None, help="Stop after N frames (fast iteration)")
    return p.parse_args()


def draw_preview(frame, boxes_xyxy, track_ids):
    for track_id, (x1, y1, x2, y2) in zip(track_ids, boxes_xyxy):
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(frame, p1, p2, (0, 230, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (p1[0], max(p1[1] - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 0), 2)
    return frame


def main():
    args = parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.model)
    decoder = M0Decoder(source=args.video, k1=args.k1)

    history: dict[int, list[tuple[int, float, float, float, float]]] = {}
    writer = None
    frame_count = 0

    for frame in decoder:
        if args.max_frames is not None and frame_count >= args.max_frames:
            break

        # persist=True is what makes this a TRACKER call instead of a one-shot detector
        # call — it keeps ultralytics' internal BYTETracker state (existing tracks,
        # their Kalman filters, track_buffer age counters) alive across this loop.
        result = model.track(
            frame.data, persist=True, tracker=args.tracker,
            classes=[PERSON_CLASS], conf=args.conf, imgsz=args.imgsz, verbose=False,
        )[0]

        boxes_xyxy, track_ids = [], []
        if result.boxes.id is not None:
            boxes_xyxy = [tuple(b) for b in result.boxes.xyxy.tolist()]
            track_ids = [int(t) for t in result.boxes.id.tolist()]

        accumulate_track_history(history, frame.frame_idx, boxes_xyxy, track_ids)

        if args.preview_video:
            disp = draw_preview(frame.data.copy(), boxes_xyxy, track_ids)
            if writer is None:
                h, w = disp.shape[:2]
                writer = cv2.VideoWriter(
                    args.preview_video, cv2.VideoWriter_fourcc(*"mp4v"), 25, (w, h)
                )
            writer.write(disp)

        frame_count += 1

    if writer is not None:
        writer.release()

    out_xml = out_dir / "annotations.xml"
    boxes_to_cvat_xml(history, total_frames=frame_count, out_path=out_xml)
    print(f"Processed {frame_count} frames, {len(history)} tracks -> {out_xml}")
    if args.preview_video:
        print(f"Preview video -> {args.preview_video}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test on a short slice of a real video (fast iteration, not the final run)**

Run:
```bash
python3 -m tracking.run_tracker dataset/2026-06-10/00-52-57.mp4 \
    --output annotations/00-52-57_smoke --max-frames 50 \
    --preview-video annotations/00-52-57_smoke/preview.mp4
```
Expected: no traceback; final line like `Processed 50 frames, N tracks -> annotations/00-52-57_smoke/annotations.xml`.
If it errors on `result.boxes.id` being `None` on frame 0 with zero people in frame —
that's expected/handled (the `if result.boxes.id is not None` guard exists for exactly
this: the tracker has no confirmed tracks yet on the very first frames, or on any frame
with zero detections).

- [ ] **Step 3: Commit**

```bash
git add tracking/run_tracker.py
git commit -m "Wire CLI: M0Decoder -> model.track(persist=True) -> CVAT export"
```

---

## Task 6: Full run + visual verification

**Files:** none (this is the verification pass, per
`superpowers:verification-before-completion` — evidence before claiming this is done).

- [ ] **Step 1: Run on a full real video (no `--max-frames`)**

```bash
python3 -m tracking.run_tracker dataset/2026-06-10/00-52-57.mp4 \
    --output annotations/00-52-57 \
    --preview-video annotations/00-52-57/preview.mp4
```
Expected: completes without error; `annotations/00-52-57/annotations.xml` and
`preview.mp4` both exist and are non-empty.

- [ ] **Step 2: Watch `preview.mp4` and evaluate against Task 2's checkpoint, not against a "zero ID switches" bar**

What you're checking for:
  - When two people walk without crossing paths, does the `ID N` label stay the same
    number the whole time? (If not, something's wrong with the tracker call itself —
    stop and re-check Task 5's `persist=True` wiring before going further.)
  - When someone is briefly occluded (walks behind another person/object) and re-emerges,
    does the ID re-attach, or does a new ID appear? Either outcome is informative: ID
    re-attaches → ByteTrack's 2-phase low-confidence matching (Task 2, Step 2.4) worked as
    designed. New ID appears → the occlusion was long/total enough to exceed `track_buffer`
    frames, which is exactly the kind of case the annotator fixes by hand in CVAT — this
    is expected v1 behavior, not a bug (see spec's "Ngoài phạm vi": ReID would reduce this,
    and is explicitly deferred).

- [ ] **Step 3: Sanity-check the XML is well-formed and matches expectations**

```bash
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('annotations/00-52-57/annotations.xml')
tracks = tree.getroot().findall('track')
print(f'{len(tracks)} tracks')
for t in tracks[:3]:
    boxes = t.findall('box')
    print(f\"  track {t.get('id')}: {len(boxes)} boxes, last outside={boxes[-1].get('outside')}\")
"
```
Expected: prints a track count > 0 and per-track box counts that look plausible for the
video's length and number of people.

- [ ] **Step 4: If you have a CVAT instance available, import `annotations.xml` into a video task and confirm it loads without a format error**

This step is optional if no CVAT instance is set up yet — the format has already been
validated structurally by Task 3's test; this step only confirms CVAT's own parser
accepts it.

---

## Estimate

| Task | What | Est. time |
|---|---|---|
| 1 | Scaffold + deps | 10–15 min |
| 2 | Read ultralytics source, build real understanding | 40–60 min (the actual "learning" bulk of the session) |
| 3 | `cvat_export.py` + TDD | 25–35 min |
| 4 | `accumulate_track_history` + TDD | 15–20 min |
| 5 | CLI wiring + smoke test | 30–45 min (includes first-run debugging: import paths, model load time, tuning `--max-frames`) |
| 6 | Full run + visual verification | 15–30 min (depends on video length and GPU speed) |
| **Total** | | **~2.5–3.5 hours** of focused session time |

Biggest variables: how long Task 2's reading/discussion actually takes (this is the part
that can't be rushed without defeating the point of the session), and Task 6's video
length/GPU speed for the full-video pass. Nothing here requires downloading models —
`yolo26{n,s,m,l}.pt` are already present at the project root.
