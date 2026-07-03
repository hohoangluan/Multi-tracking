"""
CVAT Video 1.1 XML exporter.

Format reference (schema CVAT expects for a video annotation task import):

    <annotations>
      <version>1.1</version>
      <track id="1" label="person">
        <box frame="0" xtl="10.00" ytl="10.00" xbr="50.00" ybr="90.00"
             outside="0" occluded="0" keyframe="1"/>
        ...
        <box frame="42" xtl="0.00" ytl="0.00" xbr="0.00" ybr="0.00"
             outside="1" occluded="0" keyframe="1"/>
      </track>
    </annotations>

`outside="1"` is CVAT's explicit "this track stops existing at this frame" marker —
without it, CVAT interpolates the box forward past where the person actually left the
tracked region. We add exactly one outside=1 box, one frame after a track's last real
detection, unless that track survived to the very last frame of the clip.

Targets Python 3.8: no `ET.indent()` (3.9+) — output is unformatted but valid XML,
which CVAT parses fine.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def boxes_to_cvat_xml(
    history: dict[int, list[tuple[int, float, float, float, float]]],
    total_frames: int,
    out_path: str | Path,
    label: str = "person",
) -> None:
    root = ET.Element("annotations")
    ET.SubElement(root, "version").text = "1.1"

    for track_id in sorted(history):
        frames = sorted(history[track_id], key=lambda f: f[0])
        track_el = ET.SubElement(root, "track", id=str(track_id), label=label)

        for frame_idx, x1, y1, x2, y2 in frames:
            ET.SubElement(
                track_el, "box",
                frame=str(frame_idx),
                xtl=f"{x1:.2f}", ytl=f"{y1:.2f}", xbr=f"{x2:.2f}", ybr=f"{y2:.2f}",
                outside="0", occluded="0", keyframe="1",
            )

        last_frame = frames[-1][0]
        end_frame = last_frame + 1
        if end_frame < total_frames:
            ET.SubElement(
                track_el, "box",
                frame=str(end_frame),
                xtl="0.00", ytl="0.00", xbr="0.00", ybr="0.00",
                outside="1", occluded="0", keyframe="1",
            )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)