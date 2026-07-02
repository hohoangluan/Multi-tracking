import unittest

from tracking.run_tracker import accumulate_track_history


class TestAccumulateTrackHistory(unittest.TestCase):
    def test_appends_per_track_across_frames_and_ignores_absent_ids(self):
        history: dict = {}

        # Frame 0: two people, track ids 1 and 2.
        accumulate_track_history(
            history, frame_idx=0,
            boxes_xyxy=[(10.0, 10.0, 50.0, 90.0), (200.0, 20.0, 240.0, 100.0)],
            track_ids=[1, 2],
        )
        # Frame 1: only track 1 detected (track 2 occluded this frame -> caller simply
        # doesn't pass it, it is NOT this function's job to invent a box for it).
        accumulate_track_history(
            history, frame_idx=1,
            boxes_xyxy=[(12.0, 10.0, 52.0, 90.0)],
            track_ids=[1],
        )

        self.assertEqual(
            history[1],
            [(0, 10.0, 10.0, 50.0, 90.0), (1, 12.0, 10.0, 52.0, 90.0)],
        )
        self.assertEqual(history[2], [(0, 200.0, 20.0, 240.0, 100.0)])

    def test_empty_frame_is_a_no_op(self):
        history: dict = {}
        accumulate_track_history(history, frame_idx=0, boxes_xyxy=[], track_ids=[])
        self.assertEqual(history, {})


if __name__ == "__main__":
    unittest.main()