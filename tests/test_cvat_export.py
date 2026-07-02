import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from tracking.cvat_export import boxes_to_cvat_xml


class TestBoxesToCvatXml(unittest.TestCase):
    def test_two_tracks_one_disappears_early(self):
        # Track 1: present frames 0,1,2 (visible to the end of the clip, 3 frames total).
        # Track 2: present frames 0,1 only (disappears before the clip ends).
        history = {
            1: [(0, 10.0, 10.0, 50.0, 90.0), (1, 12.0, 10.0, 52.0, 90.0), (2, 14.0, 10.0, 54.0, 90.0)],
            2: [(0, 200.0, 20.0, 240.0, 100.0), (1, 202.0, 20.0, 242.0, 100.0)],
        }
        with TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "annotations.xml"
            boxes_to_cvat_xml(history, total_frames=3, out_path=out_path, label="person")

            tree = ET.parse(out_path)
            root = tree.getroot()

            self.assertEqual(root.find("version").text, "1.1")
            tracks = root.findall("track")
            self.assertEqual(len(tracks), 2)

            track_by_id = {t.get("id"): t for t in tracks}
            self.assertEqual(track_by_id["1"].get("label"), "person")

            # Track 1 stayed alive through the last frame (2) of a 3-frame clip -> no
            # outside=1 terminator needed.
            boxes_t1 = track_by_id["1"].findall("box")
            self.assertEqual(len(boxes_t1), 3)
            self.assertEqual(boxes_t1[-1].get("outside"), "0")

            # Track 2 disappeared after frame 1 (clip has frames 0,1,2) -> must get an
            # outside=1 terminator box on frame 2.
            boxes_t2 = track_by_id["2"].findall("box")
            self.assertEqual(len(boxes_t2), 3)
            self.assertEqual(boxes_t2[0].get("outside"), "0")
            self.assertEqual(boxes_t2[1].get("outside"), "0")
            self.assertEqual(boxes_t2[2].get("frame"), "2")
            self.assertEqual(boxes_t2[2].get("outside"), "1")


if __name__ == "__main__":
    unittest.main()