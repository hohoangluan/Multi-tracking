"""
Fisheye undistortion — works with or without calibration data.

Without calibration (most common case):
    u = SimpleUndistorter(image_size=(2880, 1620), k1=-0.30)
    flat = u.undistort(frame)

With calibration file (from calibrate.py):
    u = load_undistorter("calibration.npz")
    flat = u.undistort(frame)
"""

from __future__ import annotations  # allow tuple[...]/str | Path hints on Python 3.8

from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np


class BaseUndistorter(ABC):
    @abstractmethod
    def undistort(self, frame: np.ndarray) -> np.ndarray: ...

    @property
    @abstractmethod
    def output_size(self) -> tuple[int, int]: ...   # (width, height)


class SimpleUndistorter(BaseUndistorter):
    """
    No-calibration fisheye correction.

    Estimates the camera matrix from image dimensions (focal ≈ image width,
    principal point = center), then applies a single radial coefficient k1.

    k1 : radial distortion strength.
         Negative → barrel / fisheye correction (typical: -0.2 to -0.5).
         Positive → pincushion correction.
         Start at -0.30 and tune with --preview until straight lines look straight.

    focal_scale : multiplier on image width used to estimate focal length.
                  1.0 works for most wide-angle cameras; lower (0.7–0.9) for
                  very wide / ≥180° fisheye.
    """

    def __init__(
        self,
        image_size: tuple[int, int],   # (width, height)
        k1: float = -0.30,
        focal_scale: float = 1.0,
    ):
        w, h = image_size
        f = w * focal_scale
        self._K = np.array([[f, 0, w / 2],
                             [0, f, h / 2],
                             [0, 0, 1]], dtype=np.float64)
        # D for standard (Brown-Conrady) model: (k1, k2, p1, p2)
        self._D = np.array([k1, 0.0, 0.0, 0.0], dtype=np.float64)
        self._image_size = image_size

        new_K, roi = cv2.getOptimalNewCameraMatrix(
            self._K, self._D, image_size, alpha=0
        )
        self._new_K = new_K
        self._roi = roi

        self._map1, self._map2 = cv2.initUndistortRectifyMap(
            self._K, self._D, None, new_K, image_size, cv2.CV_16SC2
        )

    def undistort(self, frame: np.ndarray) -> np.ndarray:
        out = cv2.remap(frame, self._map1, self._map2,
                        interpolation=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT)
        x, y, w, h = self._roi
        if w > 0 and h > 0:
            out = out[y: y + h, x: x + w]
        return out

    @property
    def output_size(self) -> tuple[int, int]:
        x, y, w, h = self._roi
        return (w, h) if w > 0 else self._image_size


class FisheyeUndistorter(BaseUndistorter):
    """
    Kannala-Brandt fisheye model — requires calibration K, D (4 coefficients).
    Use when you have a calibration.npz from calibrate.py.
    """

    def __init__(self, K, D, image_size: tuple[int, int], alpha: float = 0.0):
        self.K = K.astype(np.float64)
        self.D = D.astype(np.float64)
        self._image_size = image_size

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            self.K, self.D, image_size, np.eye(3), balance=alpha
        )
        self._new_K = new_K
        self._map1, self._map2 = cv2.fisheye.initUndistortRectifyMap(
            self.K, self.D, np.eye(3), new_K, image_size, cv2.CV_16SC2
        )

    def undistort(self, frame: np.ndarray) -> np.ndarray:
        return cv2.remap(frame, self._map1, self._map2,
                         interpolation=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT)

    @property
    def output_size(self) -> tuple[int, int]:
        return self._image_size


class StandardUndistorter(BaseUndistorter):
    """Brown-Conrady model — requires calibration K, D."""

    def __init__(self, K, D, image_size: tuple[int, int], alpha: float = 0.0):
        self.K = K.astype(np.float64)
        self.D = D.astype(np.float64)
        self._image_size = image_size

        new_K, roi = cv2.getOptimalNewCameraMatrix(K, D, image_size, alpha)
        self._new_K = new_K
        self._roi = roi
        self._map1, self._map2 = cv2.initUndistortRectifyMap(
            K, D, None, new_K, image_size, cv2.CV_16SC2
        )

    def undistort(self, frame: np.ndarray) -> np.ndarray:
        out = cv2.remap(self._map1, self._map2,
                        interpolation=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT)
        x, y, w, h = self._roi
        if w > 0 and h > 0:
            out = out[y: y + h, x: x + w]
        return out

    @property
    def output_size(self) -> tuple[int, int]:
        x, y, w, h = self._roi
        return (w, h) if w > 0 else self._image_size


def load_undistorter(path: str | Path, alpha: float = 0.0) -> BaseUndistorter:
    """Load calibration.npz produced by calibrate.py."""
    data = np.load(path)
    K, D = data["K"], data["D"]
    image_size = tuple(int(v) for v in data["image_size"])
    model = str(data["model"])

    if model == "fisheye":
        return FisheyeUndistorter(K, D, image_size, alpha)
    elif model == "standard":
        return StandardUndistorter(K, D, image_size, alpha)
    else:
        raise ValueError(f"Unknown model in calibration file: {model!r}")
