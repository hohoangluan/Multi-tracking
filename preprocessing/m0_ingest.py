"""
M0 — Video Decode + Fisheye Undistortion

Responsibilities (ONLY):
  1. Open video source (file / RTSP) with hardware acceleration hint (NVDEC).
  2. Apply fisheye correction to each decoded frame.
  3. Yield flat (rectilinear) frames with timestamp — one per source frame.

Everything downstream (frame selection, detection scheduling, Kalman) is handled
by later modules. M0 is deliberately thin so those concerns don't bleed in here.

Usage:
  # Default correction (k1=-0.30, no calibration file needed):
  for frame in M0Decoder("video.mp4"):
      process(frame.data, frame.timestamp_ms)

  # With calibration file:
  for frame in M0Decoder("video.mp4", calib="calibration.npz"):
      process(frame.data, frame.timestamp_ms)

  # CLI — preview or dump:
  python3 -m preprocessing.m0_ingest dataset/2026-06-10/00-52-57.mp4 --preview
  python3 -m preprocessing.m0_ingest dataset/2026-06-10/00-52-57.mp4 --output frames/
"""

from __future__ import annotations

import argparse
import logging
import queue
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from typing import Generator, Optional

import cv2
import numpy as np

from .undistort import BaseUndistorter, SimpleUndistorter, load_undistorter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class DecodedFrame:
    data:         np.ndarray   # BGR undistorted full-res frame  →  M1/M2 input
    frame_idx:    int          # index in source video (0-based)
    timestamp_ms: float        # video timestamp in ms — used for cross-cam sync (M7)
    source:       str          # path/URL, for multi-camera bookkeeping


# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------

class M0Decoder:
    """
    Video decoder with fisheye correction.

    Parameters
    ----------
    source : file path or RTSP URL
    k1     : radial distortion coefficient when no calib file is given.
             Negative → barrel/fisheye correction. Tune with --preview.
             Typical range for security fisheye cams: -0.2 to -0.5.
    calib  : path to calibration.npz (from calibrate.py). When provided, k1 is ignored.
    undistort : set False to skip correction entirely (raw decode only).
    """

    def __init__(
        self,
        source:    str,
        k1:        float           = -0.30,
        focal_scale: float         = 1.0,
        calib:     Optional[str]   = None,
        undistort: bool            = True,
        ring_size: int             = 64,    # async queue depth (M0 spec param)
    ):
        self._source     = source
        self._k1         = k1
        self._focal_scale = focal_scale
        self._calib      = calib
        self._undistort  = undistort
        self._ring_size  = ring_size
        self._corrector: Optional[BaseUndistorter] = None

    # ------------------------------------------------------------------ #
    # Generator interface                                                  #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Generator[DecodedFrame, None, None]:
        cap = self._open()
        self._corrector = None   # built lazily from first frame (need image size)

        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                flat  = self._correct(frame)

                yield DecodedFrame(
                    data=flat,
                    frame_idx=frame_idx,
                    timestamp_ms=ts_ms,
                    source=self._source,
                )
                frame_idx += 1
        finally:
            cap.release()

    # ------------------------------------------------------------------ #
    # Async interface (background thread + ring buffer queue)             #
    # ------------------------------------------------------------------ #

    def start_async(self) -> "queue.Queue[Optional[DecodedFrame]]":
        """
        Start decoding in a daemon thread.
        Returns a queue; get() yields DecodedFrame objects until None (end-of-stream).
        """
        q: queue.Queue = queue.Queue(maxsize=self._ring_size)

        def _worker():
            for frame in self:
                q.put(frame)
            q.put(None)

        Thread(target=_worker, daemon=True).start()
        return q

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _open(self) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(self._source, cv2.CAP_FFMPEG)
        # Request hardware acceleration (NVDEC/VAAPI/DXVA depending on platform).
        # OpenCV uses it silently if the build supports it; otherwise falls back
        # to software decode — no code change needed for either case.
        cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)

        if not cap.isOpened():
            raise RuntimeError(f"M0: cannot open source: {self._source!r}")

        hw = cap.get(cv2.CAP_PROP_HW_ACCELERATION)
        logger.info(
            "M0: opened %s  [%s decode]  %.0f fps",
            self._source,
            "HW (NVDEC)" if hw != cv2.VIDEO_ACCELERATION_NONE else "software CPU",
            cap.get(cv2.CAP_PROP_FPS) or 0,
        )
        return cap

    def _correct(self, frame: np.ndarray) -> np.ndarray:
        """Build undistorter on first call (needs image size), then apply."""
        if not self._undistort:
            return frame

        if self._corrector is None:
            h, w = frame.shape[:2]
            if self._calib:
                self._corrector = load_undistorter(self._calib)
                logger.info("M0: loaded calibration from %s", self._calib)
            else:
                self._corrector = SimpleUndistorter(
                    image_size=(w, h),
                    k1=self._k1,
                    focal_scale=self._focal_scale,
                )
                logger.info("M0: using estimated correction  k1=%.3f  focal_scale=%.2f",
                            self._k1, self._focal_scale)

        return self._corrector.undistort(frame)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args():
    p = argparse.ArgumentParser(description="M0 — decode + fisheye correction")
    p.add_argument("source", help="Video file or RTSP URL")
    p.add_argument("--output", "-o", default=None,
                   help="Directory to save undistorted frames as JPEG")
    p.add_argument("--k1", type=float, default=-0.30,
                   help="Radial distortion coefficient (default: -0.30)")
    p.add_argument("--focal-scale", type=float, default=1.0)
    p.add_argument("--calib", default=None,
                   help="Path to calibration.npz (overrides --k1)")
    p.add_argument("--no-undistort", action="store_true",
                   help="Skip correction, raw decode only")
    p.add_argument("--quality", type=int, default=92,
                   help="JPEG quality when saving (default: 92)")
    p.add_argument("--preview", action="store_true",
                   help="Show live preview (press Q to quit)")
    return p.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    args = _parse_args()

    out_dir = Path(args.output) if args.output else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, args.quality]

    decoder = M0Decoder(
        source=args.source,
        k1=args.k1,
        focal_scale=args.focal_scale,
        calib=args.calib,
        undistort=not args.no_undistort,
    )

    count = 0
    t0 = time.perf_counter()

    for frame in decoder:
        count += 1

        if out_dir:
            path = out_dir / f"frame_{frame.frame_idx:06d}.jpg"
            cv2.imwrite(str(path), frame.data, jpeg_params)

        if args.preview:
            disp = cv2.resize(frame.data, (960, 540))
            cv2.putText(disp,
                        f"frame {frame.frame_idx}  t={frame.timestamp_ms/1000:.2f}s",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("M0 — undistorted", disp)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()
    elapsed = time.perf_counter() - t0
    print(f"\nDecoded {count} frames in {elapsed:.1f}s  ({count/elapsed:.1f} fps)")
    if out_dir:
        print(f"Saved → {out_dir}")


if __name__ == "__main__":
    main()
