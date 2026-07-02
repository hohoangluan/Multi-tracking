# Thiết kế: Tracker (ByteTrack qua ultralytics) + xuất CVAT cho semi-auto annotation

Ngày: 2026-07-02
Trạng thái: đã duyệt bởi user, chờ viết implementation plan

## Bối cảnh

Pipeline hiện có (đã chạy được):
- `preprocessing/m0_ingest.py` — `M0Decoder`: decode video + sửa méo fisheye (không cần
  file calibration), sinh ra `DecodedFrame{data, frame_idx, timestamp_ms, source}`.
- `preprocessing/undistort.py` — `SimpleUndistorter` (ước lượng K từ kích thước ảnh + k1)
  và các biến thể dùng calibration thật.
- `person_dectection/detect.py` — detect người bằng YOLO26 (`ultralytics`), lọc sẵn
  `classes=[0]`.
- `web_demo/app.py` — demo trực quan live, không liên quan tới annotation.

Còn thiếu: **M3 — single-cam tracking** (theo `pipeline_detail.md`, mục tiêu cuối là
BoT-SORT-ReID, nhưng ReID/appearance/calibration world-space **không nằm trong phạm vi
phiên này** — xem mục Ngoài phạm vi).

Mục tiêu phiên này: xây pipeline **semi-automatic annotation** — detector + tracker gán
sẵn ID cho người qua các frame, xuất ra định dạng CVAT, để người gán nhãn chỉ cần sửa
ID-switch / fragmentation / box sai, thay vì vẽ box từ đầu.

## Mục tiêu & phạm vi

- Dùng **`ultralytics` `model.track()`** (đã có sẵn trong dependency, bản 8.4.75) với
  tracker `bytetrack.yaml` tích hợp sẵn — **không tự viết tay** Kalman filter / cost
  matrix / Hungarian / logic 2-pha matching. Lý do: `ultralytics` đã implement đúng
  ByteTrack (Kalman + Hungarian qua `scipy.optimize.linear_sum_assignment` + 2-pha
  matching high-conf/low-conf) — viết lại là trùng lặp không cần thiết.
- Thành phần "dạy học" (yêu cầu rõ của user: hiểu code, không vibecode) nằm ở việc **đọc
  trực tiếp source code đã cài** của `ultralytics` cùng nhau, không chỉ gọi API:
  - `ultralytics/trackers/byte_tracker.py` — vòng lặp `BYTETracker.update()`.
  - `ultralytics/trackers/utils/kalman_filter.py` — bước `predict()`/`update()`.
  - `ultralytics/trackers/utils/matching.py` — `iou_distance()`, `linear_assignment()`.
  - `ultralytics/cfg/trackers/bytetrack.yaml` — ý nghĩa từng tham số
    (`track_high_thresh`, `track_low_thresh`, `new_track_thresh`, `track_buffer`,
    `match_thresh`).
- Chạy end-to-end trên **một video thật** trong `dataset/2026-06-10/*.mp4` (không dùng
  `frames_test/`) — vì mục tiêu là annotation thật, không phải bài tập tách rời.
- Xuất kết quả ra **CVAT Video 1.1 XML** (`<track><box frame=".." xtl=".." outside=".."/>`),
  dùng `xml.etree.ElementTree` từ stdlib — không có thư viện chuẩn nào tạo đúng định
  dạng annotator cần theo đúng ý (buffer track đã "chết", đánh dấu `outside`), nên viết
  tay phần này, có giải thích rõ từng field XML nghĩa là gì.

## Ngoài phạm vi (rõ ràng, để tránh lan phạm vi)

- ReID / appearance embedding (OSNet) — `bytetrack.yaml` không có ReID; nếu cần
  BoT-SORT-ReID thật như `pipeline_detail.md` mô tả, đó là phiên sau, đổi
  `tracker="botsort.yaml"` + bật `with_reid`.
- Calibration thật / world-space projection (M1 nâng cao) — vẫn dùng
  `SimpleUndistorter` ước lượng như hiện tại.
- Multi-camera association (M7+), toàn bộ scaffold `mtmc/` cũ (đã bị xoá khỏi working
  tree, không khôi phục).
- Tinh chỉnh threshold trong `bytetrack.yaml` cho riêng video của user — có thể làm sau
  khi thấy kết quả v1, không phải điều kiện để coi phiên này "xong".

## Kiến trúc / luồng dữ liệu

```
video (dataset/2026-06-10/XX-XX-XX.mp4)
   │
   ▼  preprocessing.m0_ingest.M0Decoder   (đã có, tái sử dụng nguyên bản)
DecodedFrame{data, frame_idx, timestamp_ms}
   │
   ▼  model.track(frame.data, persist=True, tracker="bytetrack.yaml",
   │              classes=[0], conf=..., imgsz=...)
Results.boxes  {xyxy, conf, id}   ← id do ultralytics gán, giữ nguyên qua các frame
   │                                nhờ persist=True (tracker giữ state nội bộ)
   ▼  gom theo track_id
dict[track_id -> list[(frame_idx, x1, y1, x2, y2)]]
   │
   ▼  tracking.cvat_export.boxes_to_cvat_xml()
annotations.xml   (CVAT Video 1.1, sẵn sàng import + sửa tay trong CVAT)
```

Ghi chú quan trọng: `model.track()` được gọi **từng frame một** (không truyền
`source=video_path` cho ultralytics tự decode), vì cần chèn bước undistort của
`M0Decoder` **trước** khi đưa frame vào detector — đúng thứ tự M0 → M1 → M2 → M3 đã định
trong `pipeline_detail.md`. Frame nào ultralytics **không track được ai** (0 box) vẫn
phải gọi `model.track()` với `persist=True` để bộ đếm `age`/`track_buffer` nội bộ của
tracker tăng đúng — không được skip frame.

## Thành phần / file cụ thể

```
tracking/
├── __init__.py
├── run_tracker.py     # CLI orchestrator (mô tả bên dưới)
└── cvat_export.py     # boxes_to_cvat_xml(tracks, frame_w, frame_h, total_frames, out_path)
```

### `run_tracker.py`

CLI, phong cách giống `preprocessing/pipeline.py` (argparse, không OOP thừa):

```
python3 -m tracking.run_tracker dataset/2026-06-10/00-52-57.mp4 \
    --output annotations/00-52-57 \
    --model yolo26m.pt --conf 0.3 --imgsz 960 \
    --tracker bytetrack.yaml \
    --preview-video annotations/00-52-57/preview.mp4
```

- Dùng lại `M0Decoder` để lấy frame đã undistort.
- Load model 1 lần (`YOLO(args.model)`), gọi `model.track(frame.data, persist=True, ...)`
  trong vòng lặp.
- Gom `dict[track_id -> list[(frame_idx, bbox)]]` — track đã "biến mất" (không match được
  nữa) vẫn giữ trong dict, không xoá, vì CVAT export cần biết track kết thúc ở frame nào.
- Cờ `--preview-video`: dùng `cv2.VideoWriter` vẽ box + track_id lên từng frame, ghi ra
  video mp4 — dùng để soi bằng mắt trước khi mở CVAT (mục tiêu: thấy ID-switch/fragment ở
  đâu, có hợp lý để sửa tay không).
- Cuối cùng gọi `boxes_to_cvat_xml(...)`.

### `cvat_export.py`

- Input: dict track_id → list các `(frame_idx, x1, y1, x2, y2)`, kích thước frame, tổng số
  frame.
- Output: file XML theo schema CVAT Video 1.1:
  ```xml
  <annotations>
    <version>1.1</version>
    <track id="1" label="person">
      <box frame="0" xtl="100.0" ytl="200.0" xbr="150.0" ybr="300.0" outside="0" occluded="0" keyframe="1"/>
      ...
      <box frame="42" xtl="0" ytl="0" xbr="0" ybr="0" outside="1" occluded="0" keyframe="1"/>
    </track>
  </annotations>
  ```
- Với mỗi track, frame nào có bbox thật → `outside="0"`; ngay sau frame cuối cùng track
  còn sống → thêm 1 `<box outside="1">` để báo CVAT "track kết thúc ở đây, đừng nội suy
  tiếp" (đây là quy ước bắt buộc của format CVAT, không phải tuỳ chọn — sẽ giải thích kỹ
  khi viết phần này).

## Kiểm thử / xác nhận đúng

- Không cần unit test cho logic matching (đã giao cho `ultralytics`, đã có test riêng của
  họ) — trọng tâm kiểm thử nằm ở **phần mình tự viết**: `cvat_export.py`.
- Unit test `boxes_to_cvat_xml()` bằng dữ liệu giả nhỏ (2 track, vài frame, 1 track "biến
  mất" giữa chừng) → parse lại XML vừa ghi bằng `xml.etree.ElementTree`, assert đúng số
  `<track>`, đúng frame có `outside="1"`.
- Xác nhận thật: chạy `run_tracker.py` trên 1 video thật trong `dataset/`, xem
  `--preview-video` bằng mắt — chấp nhận có ID-switch (đúng kỳ vọng của `bytetrack.yaml`
  không ReID), miễn track_id ổn định khi người đi thẳng không cắt nhau. Sau đó thử import
  `annotations.xml` vào CVAT nếu user có instance CVAT sẵn để xác nhận format load được.

## Việc dạy học đi kèm (không tách khỏi implementation plan)

Khi viết implementation plan, mỗi bước code phải đi kèm bước "đọc source ultralytics
tương ứng trước khi gọi", theo đúng thứ tự trong mục Mục tiêu & phạm vi ở trên. Đây là
yêu cầu cứng của user ("teach me code not just vibecode"), không phải note phụ.
