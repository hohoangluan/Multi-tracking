"""
Person detection using YOLO26l.
Output: bounding boxes (x1,y1,x2,y2), confidence, and optionally an annotated image.

Usage:
  python3 detect.py <image_path> [options]

Options:
  --conf        Confidence threshold       (default: 0.25)
  --iou         NMS IoU threshold          (default: 0.45)
  --imgsz       Inference image size       (default: 640)
  --save        Save annotated image       (default: False)
  --output-dir  Output directory for saved images (default: ./outputs)
  --json        Print results as JSON      (default: False)
"""

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from ultralytics import YOLO

PERSON_CLASS = 0  # COCO class 0 = person


def parse_args():
    p = argparse.ArgumentParser(description="YOLO26l person detector")
    p.add_argument("image", help="Path to input image")
    p.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    p.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    p.add_argument("--imgsz", type=int, default=640, help="Inference image size (pixels)")
    p.add_argument("--save", action="store_true", help="Save annotated image to output-dir")
    p.add_argument("--output-dir", default="outputs", help="Directory to save annotated images")
    p.add_argument("--json", dest="as_json", action="store_true", help="Print detections as JSON")
    return p.parse_args()


def load_model(imgsz: int) -> YOLO:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = YOLO("yolo26m.pt")
    model.to(device)

    # Warm-up: run one dummy inference so the first real call isn't penalised
    # by CUDA kernel compilation / memory allocation.
    model.predict(
        source="https://ultralytics.com/images/bus.jpg",
        imgsz=imgsz,
        classes=[PERSON_CLASS],
        half=device == "cuda",   # FP16 only on GPU
        verbose=False,
    )
    return model


def detect(model: YOLO, image_path: str, args) -> list[dict]:
    device = next(model.model.parameters()).device.type
    t0 = time.perf_counter()

    results = model.predict(
        source=image_path,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        classes=[PERSON_CLASS],   # skip every other class before NMS → much faster
        half=device == "cuda",    # FP16 halves VRAM and speeds up GPU inference
        augment=False,            # TTA disabled for speed
        agnostic_nms=True,        # single-class NMS is slightly faster
        max_det=300,
        verbose=False,
        save=args.save,
        project=args.output_dir if args.save else None,
        name=".",
        exist_ok=True,
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000

    boxes = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes.append({
                "x1": round(x1, 1),
                "y1": round(y1, 1),
                "x2": round(x2, 1),
                "y2": round(y2, 1),
                "conf": round(float(box.conf[0]), 4),
                "w": round(x2 - x1, 1),
                "h": round(y2 - y1, 1),
            })

    # Sort by confidence descending
    boxes.sort(key=lambda b: b["conf"], reverse=True)

    return boxes, elapsed_ms


def print_boxes(boxes: list[dict], image_path: str, elapsed_ms: float):
    print(f"\nImage : {image_path}")
    print(f"Persons detected: {len(boxes)}  |  inference: {elapsed_ms:.1f} ms\n")
    if not boxes:
        print("  (none)")
        return
    header = f"{'#':>4}  {'x1':>7}  {'y1':>7}  {'x2':>7}  {'y2':>7}  {'W':>7}  {'H':>7}  {'Conf':>6}"
    print(header)
    print("-" * len(header))
    for i, b in enumerate(boxes, 1):
        print(
            f"{i:>4}  {b['x1']:>7.1f}  {b['y1']:>7.1f}  {b['x2']:>7.1f}  "
            f"{b['y2']:>7.1f}  {b['w']:>7.1f}  {b['h']:>7.1f}  {b['conf']:>6.4f}"
        )
    print()


def main():
    args = parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    model = load_model(args.imgsz)
    boxes, elapsed_ms = detect(model, str(image_path), args)

    if args.as_json:
        print(json.dumps({"image": str(image_path), "count": len(boxes), "detections": boxes}, indent=2))
    else:
        print_boxes(boxes, str(image_path), elapsed_ms)

    if args.save:
        out_dir = Path(args.output_dir) / "."
        print(f"Annotated image saved to: {out_dir / image_path.name}")


if __name__ == "__main__":
    main()
