"""Shared data contracts for the whole MTMC pipeline.

Every module exchanges these types, so the step stubs all import from here.
This keeps the input/output contract between modules consistent.

Image arrays are typed as ``NDArray`` (an alias for ``Any``) so that importing
this module never requires numpy to be installed yet — handy while the pipeline
is still a scaffold of stubs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

# Placeholder for ``numpy.ndarray`` until numpy is actually wired in.
NDArray = Any


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class Mode(Enum):
    """Pipeline operating mode (drives which params/models are used)."""

    REALTIME = "realtime"
    OFFLINE = "offline"


class Tier(Enum):
    """M8 realtime decision tier."""

    AUTO = "auto"    # auto-link
    ALERT = "alert"  # send to human review
    DEFER = "defer"  # defer to offline retrieval (M9)


# --------------------------------------------------------------------------- #
# Geometry / detection
# --------------------------------------------------------------------------- #
@dataclass
class BBox:
    """Pixel-space bounding box (x1, y1) top-left, (x2, y2) bottom-right."""

    x1: float
    y1: float
    x2: float
    y2: float
    conf: float = 1.0

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def foot(self) -> "FootPoint":
        """Ground-contact pixel = bottom-center of the box."""
        return FootPoint(u=(self.x1 + self.x2) / 2.0, v=self.y2)


@dataclass
class FootPoint:
    """Ground-contact pixel (u, v) used for homography projection."""

    u: float
    v: float


@dataclass
class WorldCoord:
    """World-plane coordinate in metres, shared origin across all 3 cameras."""

    X: float
    Y: float


@dataclass
class Frame:
    """A decoded (and possibly undistorted) frame."""

    image: NDArray
    t: float          # timestamp in seconds
    cam_id: int


@dataclass
class Detection:
    """A person detection in one frame."""

    bbox: BBox
    cam_id: int
    t: float
    foot: Optional[FootPoint] = None
    world: Optional[WorldCoord] = None


# --------------------------------------------------------------------------- #
# Tracking
# --------------------------------------------------------------------------- #
@dataclass
class KalmanState:
    """World-space Kalman state (position + velocity, metres / m·s⁻¹)."""

    X: float
    Y: float
    vX: float
    vY: float


@dataclass
class Tracklet:
    """A single-camera tracklet living in world space."""

    local_id: int
    cam_id: int
    world_trajectory: list[tuple[float, float, float]] = field(default_factory=list)  # (X, Y, t)
    bbox_history: list[BBox] = field(default_factory=list)
    states: list[KalmanState] = field(default_factory=list)
    velocity: float = 0.0
    heading: float = 0.0
    age: int = 0
    time_since_update: int = 0


# --------------------------------------------------------------------------- #
# Appearance / ReID
# --------------------------------------------------------------------------- #
@dataclass
class Crop:
    """A person crop selected for feature extraction."""

    image: NDArray
    bbox: BBox
    t: float
    quality: float = 0.0


@dataclass
class FeatureVector:
    """A ReID embedding."""

    vec: NDArray
    dim: int = 0
    model: str = ""


@dataclass
class TrackletMeta:
    """Lifecycle metadata attached in M6."""

    entry_zone: Optional[str] = None
    exit_zone: Optional[str] = None
    heading: float = 0.0
    mean_velocity: float = 0.0


@dataclass
class ManagedTracklet:
    """A completed tracklet + its metadata + appearance feature (output of M6)."""

    tracklet: Tracklet
    meta: Optional[TrackletMeta] = None
    feature: Optional[FeatureVector] = None


# --------------------------------------------------------------------------- #
# Cross-camera association / decision
# --------------------------------------------------------------------------- #
@dataclass
class Candidate:
    """A gallery candidate for a query tracklet."""

    global_id: int
    managed: ManagedTracklet
    score: float = 0.0


@dataclass
class MatchScore:
    """Top-1 score + margin to top-2, used by M8 tiered routing."""

    top1: float
    margin: float
    candidate: Optional[Candidate] = None


@dataclass
class GlobalIDRecord:
    """A global identity and its history, stored in M10."""

    global_id: int
    tracklets: list[ManagedTracklet] = field(default_factory=list)
    first_seen: float = 0.0
    last_seen: float = 0.0
