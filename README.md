# MTMC — Multi-Target Multi-Camera pipeline (nhà A)

Scaffold for the calib-first, hybrid, 2-mode (realtime / offline) MTMC pipeline
described in [pipeline_detail.md](pipeline_detail.md) and visualised in
[pipeline_diagram.html](pipeline_diagram.html).

Every module is its own folder; inside each folder the processing happens
**step by step** (one `.py` file per step). Each step is currently a typed
**stub** — the signatures and docstrings define the data contract, the bodies
`raise NotImplementedError`. Imports always succeed, so you can build the logic
one step at a time.

## Layout

```
mtmc/
├── pipeline.py              # orchestrator M0→M11 (prints the flow today)
├── common/datatypes.py      # shared types: BBox, Detection, Tracklet, ManagedTracklet, ...
├── config/params.py         # RealtimeParams / OfflineParams (the param table)
├── phase1_single_cam/       # M0 decode · M1 calibrate · M2 detect · M3 track
├── phase2_features/         # M4 quality gate · M5 ReID · M6 tracklet mgmt
└── phase3_crosscam/         # M7 assoc · M8 RT decision · M9 offline · M10 store · M11 metrics
```

Each `Mx_*/` folder has its own `README.md` listing that module's steps and its
input/output contract.

## Run

No third-party deps needed to explore the scaffold:

```bash
PYTHONPATH=. python3 -m mtmc.pipeline      # prints the module flow
```

When you start implementing, install the deps in `requirements.txt`.

## How to implement a step

1. Open the module's `README.md` to see its input/output contract.
2. Open the `stepN_*.py` file — the docstring restates the spec, the signature
   fixes the types (from `mtmc.common.datatypes`).
3. Replace `raise NotImplementedError(...)` with the real logic.
4. Wire steps together in the module `__init__.py`, then in `mtmc/pipeline.py`.

## Modes

- **Realtime:** lighter models, tight gating, tiered decision (M8). Hard cases
  are deferred to offline (M9).
- **Offline:** exhaustive retrieval (M9) with ensemble ReID + re-ranking.
