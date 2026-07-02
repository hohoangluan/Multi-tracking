# Use official NVIDIA CUDA image with Python (CUDA 11.8 matches the torch cu118 wheels below)
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install Python and system dependencies
# libgl1 + libglib2.0-0 are required by OpenCV (cv2) which Ultralytics imports;
# without libgl1 you get "ImportError: libGL.so.1: cannot open shared object file"
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

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install the CUDA 11.8 build of PyTorch from the dedicated PyTorch index.
# This MUST be a separate step: --index-url replaces PyPI entirely, so packages
# that only live on PyPI (ultralytics, opencv) cannot be resolved from it.
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu118

# Install Ultralytics (pulls in OpenCV automatically) from PyPI.
# >=8.4.0 guarantees YOLO26 support (yolo26l.pt).
RUN pip install --no-cache-dir "ultralytics>=8.4.0"

# Copy the detection script
COPY detect.py .

# Create directory for models
RUN mkdir -p /app/models

# Pre-download the COCO-pretrained YOLO26l weights so the image is self-contained
# and validates YOLO26 support at build time.
# Comment out if you prefer to mount weights from the host instead.
RUN python3 -c "from ultralytics import YOLO; YOLO('yolo26l.pt')" \
    && mv /root/.config/Ultralytics/yolo26l.pt /app/models/yolo26l.pt

# Create output directory
RUN mkdir -p /app/outputs

# Point Ultralytics model cache at /app/models so the pre-downloaded weight is found
ENV YOLO_CONFIG_DIR=/app/.config/Ultralytics
RUN mkdir -p $YOLO_CONFIG_DIR \
    && ln -s /app/models/yolo26l.pt $YOLO_CONFIG_DIR/yolo26l.pt

# Set the entrypoint — CMD provides default args overridable at runtime
ENTRYPOINT ["python3", "detect.py"]
CMD ["--help"]
