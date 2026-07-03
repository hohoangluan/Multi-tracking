# GPU image for the full pre-annotation pipeline (M0 undistort + M3 ByteTrack tracking).
# Base carries CUDA 11.8 — it MUST match the torch cu118 wheels installed below, or the
# container will silently fall back to CPU.
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Python + the shared objects OpenCV (pulled in by ultralytics) needs at runtime.
# Without libgl1 you get: ImportError: libGL.so.1: cannot open shared object file
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Torch first, from the CUDA 11.8 index. --index-url REPLACES PyPI entirely, so this must
# be its own step — ultralytics/opencv (PyPI-only) cannot be resolved from this index.
RUN pip install --no-cache-dir torch torchvision \
    --index-url https://download.pytorch.org/whl/cu118

# Everything else from PyPI. lap = Hungarian assignment used by ByteTrack; opencv-python
# is pulled in automatically by ultralytics.
RUN pip install --no-cache-dir "ultralytics>=8.4.0" lap

# Code + model weights only. The videos are mounted at run time (see docker run below),
# never baked into the image.
COPY preprocessing/ ./preprocessing/
COPY tracking/ ./tracking/
COPY person_dectection/ ./person_dectection/
COPY yolo26m.pt ./yolo26m.pt

# Default job = the tracker. Override args at `docker run`; e.g.
#   docker run --gpus all -v $PWD/datasets:/data -v $PWD/out:/out reid-pipeline \
#       /data/00-52-57.mp4 --output /out/00-52-57 --frames-dir /out/00-52-57/frames
ENTRYPOINT ["python3", "-m", "tracking.run_tracker"]
CMD ["--help"]
