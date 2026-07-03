"""
Preprocessing pipeline: video → fisheye-corrected frames → ready for detect.py

Steps:
  1. Decode video (OpenCV, CPU — fine for dataset prep)
  2. Correct fisheye distortion (no calibration file needed)
  3. Save frames as JPEG at the target FPS

Usage examples:

  # Single video, save at 5 fps, default k1=-0.30:
  python3 -m preprocessing.pipeline video.mp4 --fps 5 --output ./frames

  # Preview correction on one frame before processing the whole video:
  python3 -m preprocessing.pipeline video.mp4 --fps 5 --preview

  # Tune distortion strength (negative = barrel/fisheye correction):
  python3 -m preprocessing.pipeline video.mp4 --fps 5 --k1 -0.45

  # Batch: all .mp4 in a folder:
  python3 -m preprocessing.pipeline dataset/2026-06-10/ --fps 5 --output ./frames

  # If you have a calibration file from calibrate.py:
  python3 -m preprocessing.pipeline video.mp4 --calib calibration.npz --fps 5

  # No distortion correction (just frame extraction):
  python3 -m preprocessing.pipeline video.mp4 --fps 5 --no-undistort
"""

from __future__ import annotations  # allow tuple[...]/list[...] hints on Python 3.8

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

from .undistort import SimpleUndistorter, load_undistorter

VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".ts", ".mts", ".m4v"}


def parse_args():
    p = argparse.ArgumentParser(description="Video → undistorted frames for detection")
    p.add_argument("source", help="Video file or folder of video files")
    p.add_argument("--output", "-o", default="frames",
                   help="Output root directory (default: ./frames)")
    p.add_argument("--fps", type=float, default=5.0,
                   help="Target extraction rate in frames/sec (default: 5)")
    p.add_argument("--k1", type=float, default=-0.30,
                   help="Radial distortion coefficient — negative corrects barrel/fisheye "
                        "(default: -0.30). Ignored when --calib is provided.")
    p.add_argument("--focal-scale", type=float, default=1.0,
                   help="Focal length estimate = image_width × focal-scale (default: 1.0)")
    p.add_argument("--calib",
                   help="Path to calibration.npz from calibrate.py (overrides --k1)")
    p.add_argument("--no-undistort", action="store_true",
                   help="Skip fisheye correction — extract raw frames only")
    p.add_argument("--quality", type=int, default=92,
                   help="JPEG quality 0-100 (default: 92)")
    p.add_argument("--preview", action="store_true",
                   help="Show side-by-side comparison on one frame then exit")
    p.add_argument("--start", type=float, default=0.0,
                   help="Start time in seconds (default: 0)")
    p.add_argument("--end", type=float, default=None,
                   help="End time in seconds (default: whole video)")
    p.add_argument("--workers", type=int, default=4,
                   help="Parallel JPEG-save threads (default: 4)")
    return p.parse_args()


def collect_videos(source: str) -> list[Path]:
    p = Path(source)
    if p.is_file():
        return [p]
    videos = sorted(v for v in p.iterdir() if v.suffix.lower() in VIDEO_EXTS)
    if not videos:
        raise RuntimeError(f"No video files found in: {source}")
    return videos


def make_undistorter(frame: np.ndarray, args):
    """Build the undistorter once using the first decoded frame for image_size."""
    if args.no_undistort:
        return None
    if args.calib:
        return load_undistorter(args.calib)
    h, w = frame.shape[:2]
    return SimpleUndistorter(image_size=(w, h), k1=args.k1, focal_scale=args.focal_scale)


def preview_correction(frame: np.ndarray, undistorter) -> None:
    """Show original vs undistorted side-by-side. Press any key to continue."""
    flat = undistorter.undistort(frame) if undistorter else frame
    # Resize both to same height for display
    h = 540
    def resize_h(img):
        ratio = h / img.shape[0]
        return cv2.resize(img, (int(img.shape[1] * ratio), h))

    left  = resize_h(frame)
    right = resize_h(flat)
    # Pad narrower side so heights match exactly
    diff = left.shape[0] - right.shape[0]
    if diff > 0:
        right = cv2.copyMakeBorder(right, 0, diff, 0, 0, cv2.BORDER_CONSTANT)
    elif diff < 0:
        left = cv2.copyMakeBorder(left, 0, -diff, 0, 0, cv2.BORDER_CONSTANT)

    side_by_side = np.hstack([left, right])
    cv2.putText(side_by_side, "ORIGINAL", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    cv2.putText(side_by_side, "UNDISTORTED", (left.shape[1] + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    cv2.imshow("Preview — press any key to continue, Q to quit", side_by_side)
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    if key == ord("q"):
        sys.exit(0)


def process_video(
    video_path: Path,
    output_dir: Path,
    args,
    jpeg_params: list,
    executor: ThreadPoolExecutor,
) -> dict:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"  ERROR: cannot open {video_path}")
        return {}

    src_fps  = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Step: decode every Nth frame to achieve target FPS
    step = max(1, round(src_fps / args.fps))
    actual_fps = src_fps / step

    start_frame = int(args.start * src_fps)
    end_frame   = int(args.end * src_fps) if args.end else total_frames

    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    output_dir.mkdir(parents=True, exist_ok=True)

    undistorter = None
    futures = []
    saved = 0
    frame_idx = start_frame
    t0 = time.perf_counter()

    while frame_idx < end_frame:
        # Use grab() (no decode) to skip frames — much faster than read() for every frame
        if (frame_idx - start_frame) % step != 0:
            if not cap.grab():
                break
            frame_idx += 1
            continue

        grabbed = cap.grab()
        if not grabbed:
            break
        _, frame = cap.retrieve()
        frame_idx += 1

        # Build undistorter from first frame (need image size)
        if undistorter is None and not args.no_undistort:
            undistorter = make_undistorter(frame, args)
            if args.preview:
                preview_correction(frame, undistorter)

        flat = undistorter.undistort(frame) if undistorter else frame

        out_name = output_dir / f"frame_{saved:06d}.jpg"
        # Offload JPEG encoding to thread pool (IO-bound)
        futures.append(
            executor.submit(cv2.imwrite, str(out_name), flat, jpeg_params)
        )
        saved += 1

    # Wait for all writes to finish
    for f in futures:
        f.result()

    cap.release()
    elapsed = time.perf_counter() - t0

    meta = {
        "source_video": str(video_path),
        "source_fps": src_fps,
        "target_fps": args.fps,
        "actual_fps": round(actual_fps, 2),
        "frame_step": step,
        "frames_saved": saved,
        "undistorted": not args.no_undistort,
        "k1": args.k1 if not (args.calib or args.no_undistort) else None,
        "calib_file": args.calib,
        "output_dir": str(output_dir),
        "elapsed_sec": round(elapsed, 1),
    }
    print(
        f"  {saved:>5} frames  |  {actual_fps:.1f} fps  |  {elapsed:.1f}s  →  {output_dir}"
    )
    return meta


def main():
    args = parse_args()
    jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, args.quality]
    output_root = Path(args.output)

    videos = collect_videos(args.source)
    print(f"Found {len(videos)} video(s). Target: {args.fps} fps  |  k1={args.k1}  |  output: {output_root}\n")

    all_meta = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for video in videos:
            video_out = output_root / video.stem
            print(f"Processing: {video.name}")
            meta = process_video(video, video_out, args, jpeg_params, executor)
            all_meta.append(meta)

    # Write metadata index
    meta_path = output_root / "metadata.json"
    output_root.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(all_meta, indent=2, ensure_ascii=False))

    total_frames = sum(m.get("frames_saved", 0) for m in all_meta)
    print(f"\nDone. {total_frames} frames total → {output_root}/")
    print(f"Metadata → {meta_path}")
    print(f"\nRun detection on a frame:")
    print(f"  python3 detect.py {output_root}/<video>/frame_000000.jpg")
    print(f"  python3 detect.py {output_root}/<video>/ --save")


if __name__ == "__main__":
    main()
