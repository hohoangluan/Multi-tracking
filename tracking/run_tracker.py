"""
M3 — Person tracking (ByteTrack via ultralytics) + CVAT export.

See docs/superpowers/specs/2026-07-02-bytetrack-cvat-annotation-design.md for the full
design, and Task 2 of docs/superpowers/plans/2026-07-02-bytetrack-cvat-annotation-plan.md
for how ultralytics' BYTETracker works internally (Kalman predict, 2-phase IoU matching,
Hungarian assignment) before reading the `model.track()` call below.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO

from preprocessing.m0_ingest import M0Decoder
from .cvat_export import boxes_to_cvat_xml

PERSON_CLASS = 0


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


def frame_image_path(frames_dir: Path, frame_idx: int) -> Path:
    """Path an undistorted frame is written to, named so it lines up with the CVAT XML.

    The CVAT export keys every <box> by `frame_idx` (see cvat_export.boxes_to_cvat_xml),
    and M0's own dumper uses the same `frame_%06d.jpg` pattern — so a CVAT task built from
    these images imports the annotations.xml with zero frame-offset.
    """
    return frames_dir / f"frame_{frame_idx:06d}.jpg"


def parse_args():
    p = argparse.ArgumentParser(description="M3 tracker (ByteTrack via ultralytics) -> CVAT export")
    p.add_argument("video", help="Path to source video, e.g. dataset/2026-06-10/00-52-57.mp4")
    p.add_argument("--output", "-o", required=True, help="Output directory for annotations.xml")
    p.add_argument("--model", default="yolo26m.pt", help="Ultralytics weights file (default: yolo26m.pt)")
    p.add_argument("--tracker", default="bytetrack.yaml", help="ultralytics tracker config (default: bytetrack.yaml)")
    p.add_argument("--conf", type=float, default=0.3, help="Detection confidence threshold")
    p.add_argument("--imgsz", type=int, default=960, help="Inference image size")
    p.add_argument("--k1", type=float, default=-0.30, help="Fisheye correction coefficient (see M0Decoder)")
    p.add_argument("--frames-dir", default=None,
                   help="If set, dump each undistorted frame as JPEG here (upload these to "
                        "CVAT alongside annotations.xml)")
    p.add_argument("--jpeg-quality", type=int, default=92,
                   help="JPEG quality for --frames-dir output (default: 92)")
    p.add_argument("--cvat-video", default=None,
                   help="If set, write ONE undistorted mp4 (no boxes) here as the media to "
                        "upload to CVAT. Every source frame is written exactly once, so its "
                        "frame index matches annotations.xml — a fraction of --frames-dir's size.")
    p.add_argument("--fps", type=float, default=20.0,
                   help="Frame rate stamped on --cvat-video / --preview-video output "
                        "(metadata only; does not affect frame indexing). Default: 20")
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

    frames_dir = Path(args.frames_dir) if args.frames_dir else None
    if frames_dir is not None:
        frames_dir.mkdir(parents=True, exist_ok=True)
    jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, args.jpeg_quality]

    model = YOLO(args.model)
    decoder = M0Decoder(source=args.video, k1=args.k1)

    history: dict[int, list[tuple[int, float, float, float, float]]] = {}
    writer = None        # annotated preview (boxes drawn)
    cvat_writer = None   # clean undistorted media for CVAT (no boxes)
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

        # Dump the SAME undistorted frame the boxes were computed on — so the frame images
        # and the CVAT boxes share one coordinate system and one frame index.
        if frames_dir is not None:
            cv2.imwrite(str(frame_image_path(frames_dir, frame.frame_idx)), frame.data, jpeg_params)

        # Clean undistorted media for CVAT: one write per source frame keeps the video's
        # frame index aligned with annotations.xml (no boxes burned in).
        if args.cvat_video:
            if cvat_writer is None:
                h, w = frame.data.shape[:2]
                cvat_writer = cv2.VideoWriter(
                    args.cvat_video, cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (w, h)
                )
            cvat_writer.write(frame.data)

        if args.preview_video:
            disp = draw_preview(frame.data.copy(), boxes_xyxy, track_ids)
            if writer is None:
                h, w = disp.shape[:2]
                writer = cv2.VideoWriter(
                    args.preview_video, cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (w, h)
                )
            writer.write(disp)

        frame_count += 1

    if writer is not None:
        writer.release()
    if cvat_writer is not None:
        cvat_writer.release()

    out_xml = out_dir / "annotations.xml"
    boxes_to_cvat_xml(history, total_frames=frame_count, out_path=out_xml)
    print(f"Processed {frame_count} frames, {len(history)} tracks -> {out_xml}")
    if frames_dir is not None:
        print(f"Frames -> {frames_dir}")
    if args.cvat_video:
        print(f"CVAT media video -> {args.cvat_video}")
    if args.preview_video:
        print(f"Preview video -> {args.preview_video}")


if __name__ == "__main__":
    main()