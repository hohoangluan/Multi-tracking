"""Top-level orchestrator wiring the modules M0 → M11.

This file documents the end-to-end flow for both modes. The actual wiring is
left as a TODO until the step stubs are implemented — for now ``main`` just
prints the pipeline order so you can see the data flow at a glance.

Run:
    PYTHONPATH=. python -m mtmc.pipeline
"""
from __future__ import annotations

from mtmc.common.datatypes import Mode

# Ordered flow per phase (module -> short purpose). Mirrors pipeline_detail.md.
PHASE_I = [
    ("M0", "video decode      → AI tensor (15fps)"),
    ("M1", "calibrate/undistort → flat image + world (X,Y)"),
    ("M2", "person detect      → bbox, conf"),
    ("M3", "single-cam track   → world-space tracklets"),
]
PHASE_II = [
    ("M4", "quality gate       → top-K best crops"),
    ("M5", "ReID extract       → feature vector"),
    ("M6", "tracklet mgmt      → tracklet + meta + feat"),
]
PHASE_III = [
    ("M7", "cross-cam assoc    → candidates + scores"),
    ("M8", "realtime decision  → auto / alert / defer"),
    ("M9", "offline retrieval  → global id (exhaustive)"),
    ("M10", "global id store    → gallery pool (feedback → M7)"),
    ("M11", "metrics            → IDF1 / mAP / Fβ / FP·h⁻¹"),
]


def run_realtime() -> None:
    """Realtime path: M0→M3→M4→M6→M7→M8→M10 (defers hard cases to M9)."""
    raise NotImplementedError("TODO: wire the realtime path once steps are implemented")


def run_offline() -> None:
    """Offline path: exhaustive M9 retrieval over the gallery → M10."""
    raise NotImplementedError("TODO: wire the offline path once steps are implemented")


def _print_flow() -> None:
    print("MTMC pipeline — module flow (see pipeline_detail.md)\n")
    for name, phase in (
        ("PHASE I  — single-cam preprocessing", PHASE_I),
        ("PHASE II — feature extraction & tracklet mgmt", PHASE_II),
        ("PHASE III — cross-camera association & decision", PHASE_III),
    ):
        print(name)
        for mid, desc in phase:
            print(f"  {mid:<4} {desc}")
        print()
    print(f"modes available: {[m.value for m in Mode]}")


if __name__ == "__main__":
    _print_flow()
