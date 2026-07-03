#!/usr/bin/env bash
# Run the whole pre-annotation pipeline on the GPU server.
# Usage (from the project folder on the server):  bash run_all.sh
set -e

echo "=== Building image ==="
docker compose build

echo "=== GPU check (must print: CUDA: True) ==="
docker compose run --rm --entrypoint python3 tracker \
  -c "import torch; print('CUDA:', torch.cuda.is_available())"

for v in 00-52-57 01-00-45 01-14-08; do
  echo "=== Tracking $v ==="
  docker compose run --rm tracker \
    /data/$v.mp4 --output /out/$v --frames-dir /out/$v/frames
done

echo "=== Done. Results are in ./out/ ==="
