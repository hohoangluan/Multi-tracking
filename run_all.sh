#!/usr/bin/env bash
# Run the whole pre-annotation pipeline on the GPU server.
# Usage (from the project folder on the server):  bash run_all.sh
set -e

echo "=== Building image ==="
docker compose build

echo "=== GPU check (must print: CUDA: True) ==="
docker compose run --rm --entrypoint python3 tracker \
  -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Videos live under ./dataset/<DATE>/<name>.mp4 (mounted as /data/<DATE>/<name>.mp4).
# M0 fisheye-undistortion still runs inside the tracker; we just don't dump any media
# (no --cvat-video / --frames-dir) — only annotations.xml, to save time.
DATE=2026-06-10
for v in 00-52-57 01-00-45 01-14-08; do
  echo "=== Tracking $v ==="
  docker compose run --rm tracker \
    /data/$DATE/$v.mp4 --output /out/$v
done

echo "=== Done. Results are in ./out/ ==="
