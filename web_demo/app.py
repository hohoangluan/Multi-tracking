"""
Web demo — person detection in video (fisheye undistort + YOLO26).

Live CCTV-style MJPEG stream: pick a dataset video (or upload one), the server
undistorts each frame, runs YOLO26 person detection, draws boxes + a live
person count / FPS overlay, and streams it to the browser.

Performance design (to reach ~30 FPS on an RTX 2080 Ti):
  1. RESIZE → UNDISTORT  (not undistort→resize): remap runs on the small display
     frame (~5 ms) instead of the full 2880×1620 frame (~66 ms). k1 is unchanged
     because the distortion model is normalised by the camera matrix.
  2. THREADED DECODE: a background reader keeps the latest decoded frame so video
     decode (~23 ms) overlaps with GPU inference instead of running before it.
  3. SELECTABLE MODEL: yolo26m hits ~30 FPS; yolo26l is more accurate (~24 FPS).

Run:
    cd /workingspace_aiclub/WorkingSpace/Personal/vannk/Multi-tracking
    python3 -m web_demo.app                # http://localhost:5000
    python3 -m web_demo.app --host 0.0.0.0 --port 8000   # expose on LAN
"""

from __future__ import annotations

import argparse
import queue
import threading
import time
from pathlib import Path

import cv2
import torch
from flask import (Flask, Response, render_template_string, request,
                   redirect, url_for, abort)
from ultralytics import YOLO

from preprocessing.undistort import SimpleUndistorter

# --------------------------------------------------------------------------- paths
ROOT        = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "dataset"
UPLOAD_DIR  = ROOT / "web_demo" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_EXTS  = {".mp4", ".avi", ".mkv", ".mov", ".ts", ".m4v"}

MODELS = ["yolo26n.pt", "yolo26s.pt", "yolo26m.pt", "yolo26l.pt"]
DEFAULT_MODEL = "yolo26m.pt"          # ~30 FPS; switch to yolo26l for max accuracy

# --------------------------------------------------------------------------- model(s)
DEV  = 0 if torch.cuda.is_available() else "cpu"
HALF = torch.cuda.is_available()
_models: dict = {}
_model_lock = threading.Lock()        # predict() guarded for concurrent requests


def get_model(name: str) -> YOLO:
    if name not in MODELS:
        name = DEFAULT_MODEL
    m = _models.get(name)
    if m is None:
        print(f"Loading {name} ...", flush=True)
        m = YOLO(name)
        m.predict(torch.zeros(1), classes=[0], imgsz=640, half=HALF,
                  device=DEV, verbose=False) if False else None  # (no-op placeholder)
        _models[name] = m
    return m


print(f"device={'cuda' if HALF else 'cpu'}  half={HALF}", flush=True)
get_model(DEFAULT_MODEL)              # warm default at startup

_undistorters: dict = {}


def get_undistorter(w, h, k1, fs):
    key = (w, h, round(k1, 3), round(fs, 2))
    u = _undistorters.get(key)
    if u is None:
        u = SimpleUndistorter(image_size=(w, h), k1=k1, focal_scale=fs)
        _undistorters[key] = u
    return u


# --------------------------------------------------------------------------- threaded reader
class LatestFrameReader:
    """Background decode thread; always serves the most recent frame (drops stale)
    so decode overlaps inference and the stream stays close to real time."""

    def __init__(self, src: str):
        self.cap = cv2.VideoCapture(src)
        self.q: queue.Queue = queue.Queue(maxsize=2)
        self._stop = False
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def _run(self):
        while not self._stop:
            ok, f = self.cap.read()
            if not ok:                       # loop the file
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            if self.q.full():
                try: self.q.get_nowait()
                except queue.Empty: pass
            self.q.put(f)
        self.cap.release()

    def read(self, timeout=5.0):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None

    def release(self):
        self._stop = True


# --------------------------------------------------------------------------- helpers
def list_videos():
    items = []
    for base, tag in [(DATASET_DIR, "dataset"), (UPLOAD_DIR, "upload")]:
        for p in sorted(base.rglob("*")):
            if p.suffix.lower() in VIDEO_EXTS:
                items.append((f"[{tag}] {p.relative_to(base)}", str(p)))
    return items


def safe_path(src: str) -> str:
    p = Path(src).resolve()
    if (DATASET_DIR in p.parents or UPLOAD_DIR in p.parents) and p.exists():
        return str(p)
    abort(404, "video not found / not allowed")


FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_overlay(frame, n, fps, fisheye, model):
    h, w = frame.shape[:2]
    bar = frame.copy()
    cv2.rectangle(bar, (0, 0), (w, 40), (20, 20, 20), -1)
    cv2.addWeighted(bar, 0.55, frame, 0.45, 0, frame)
    txt = (f"Persons: {n}   |   {fps:4.1f} FPS   |   "
           f"Fisheye: {'ON' if fisheye else 'OFF'}   |   {model.replace('.pt','')}")
    cv2.putText(frame, txt, (12, 27), FONT, 0.6, (0, 235, 120), 2, cv2.LINE_AA)
    return frame


def gen_stream(src, model_name, fisheye, conf, k1, fs, det_imgsz, disp_w):
    reader = LatestFrameReader(src)
    model = get_model(model_name)
    und = None
    fps_ema = 0.0
    prev = time.time()
    try:
        while True:
            frame = reader.read()
            if frame is None:
                break

            # 1) resize small FIRST  2) undistort the small frame (~13× cheaper)
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (disp_w, int(h * disp_w / w)))
            if fisheye:
                if und is None:
                    und = get_undistorter(frame.shape[1], frame.shape[0], k1, fs)
                frame = und.undistort(frame)

            with _model_lock:
                res = model.predict(frame, classes=[0], conf=conf, imgsz=det_imgsz,
                                    half=HALF, device=DEV, verbose=False)[0]

            n = len(res.boxes)
            for b in res.boxes:
                x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                cf = float(b.conf[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 230, 0), 2)
                cv2.putText(frame, f"{cf:.2f}", (x1, max(y1 - 6, 12)),
                            FONT, 0.5, (0, 230, 0), 1, cv2.LINE_AA)

            now = time.time()
            inst = 1.0 / (now - prev) if now > prev else 0.0
            prev = now
            fps_ema = inst if fps_ema == 0 else 0.9 * fps_ema + 0.1 * inst
            draw_overlay(frame, n, fps_ema, fisheye, model_name)

            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + buf.tobytes() + b"\r\n")
    finally:
        reader.release()


# --------------------------------------------------------------------------- flask
app = Flask(__name__)

PAGE = """
<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Person Detection Demo — YOLO26</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root{--bg:#0e1117;--panel:#171c26;--accent:#00eb78;--txt:#e6e6e6;--mut:#8a93a6}
  *{box-sizing:border-box}
  body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}
  header{padding:16px 22px;border-bottom:1px solid #222a38;display:flex;align-items:center;gap:12px}
  header h1{font-size:18px;margin:0;font-weight:650}
  header .dot{width:10px;height:10px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}
  .wrap{display:flex;gap:18px;padding:18px;flex-wrap:wrap}
  .panel{background:var(--panel);border:1px solid #222a38;border-radius:12px;padding:16px}
  .controls{width:300px;flex:0 0 auto}
  .stage{flex:1 1 560px;min-width:340px;display:flex;flex-direction:column;align-items:center;justify-content:center}
  label{display:block;font-size:12px;color:var(--mut);margin:14px 0 6px;text-transform:uppercase;letter-spacing:.04em}
  select,input[type=file]{width:100%;padding:9px;background:#0e131c;border:1px solid #2a3344;border-radius:8px;color:var(--txt)}
  .row{display:flex;align-items:center;gap:10px;margin-top:14px}
  .row input[type=range]{flex:1}
  .row .val{width:48px;text-align:right;color:var(--accent);font-variant-numeric:tabular-nums}
  .switch{display:flex;align-items:center;gap:8px;margin-top:14px;cursor:pointer}
  button{width:100%;margin-top:18px;padding:12px;border:0;border-radius:9px;background:var(--accent);color:#07210f;font-weight:700;cursor:pointer;font-size:15px}
  button:hover{filter:brightness(1.08)}
  .feed{width:100%;border-radius:12px;border:1px solid #222a38;background:#000;max-height:78vh}
  .hint{color:var(--mut);font-size:12px;margin-top:10px;text-align:center}
  form.up{margin-top:18px;border-top:1px solid #222a38;padding-top:14px}
  .up button{background:#27314a;color:#cdd6e6}
</style></head><body>
<header><span class="dot"></span><h1>Person Detection — Fisheye Undistort + YOLO26</h1></header>
<div class="wrap">
  <div class="panel controls">
    <label>Video nguồn</label>
    <select id="video">
      {% for label, path in videos %}<option value="{{path}}">{{label}}</option>{% endfor %}
    </select>

    <label>Model (tốc độ ↔ độ chính xác)</label>
    <select id="model">
      <option value="yolo26n.pt">yolo26n — nhanh nhất</option>
      <option value="yolo26s.pt">yolo26s</option>
      <option value="yolo26m.pt" selected>yolo26m — ~30 FPS (khuyến nghị)</option>
      <option value="yolo26l.pt">yolo26l — chính xác nhất (~24 FPS)</option>
    </select>

    <label>Confidence</label>
    <div class="row"><input id="conf" type="range" min="0.10" max="0.90" step="0.05" value="0.30"
         oninput="cv.textContent=this.value"><span class="val" id="cv">0.30</span></div>

    <label>Độ phân giải xử lý (rộng)</label>
    <div class="row"><input id="dispw" type="range" min="480" max="1280" step="160" value="960"
         oninput="dv.textContent=this.value"><span class="val" id="dv">960</span></div>

    <div class="switch"><input id="fisheye" type="checkbox" checked>
      <span>Sửa méo fisheye (k1=-0.30)</span></div>

    <button onclick="startStream()">▶ Bắt đầu</button>

    <form class="up" action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data">
      <label>…hoặc tải video lên</label>
      <input type="file" name="file" accept="video/*" required>
      <button type="submit">⬆ Upload</button>
    </form>
  </div>

  <div class="panel stage">
    <img id="feed" class="feed" src="" alt="Nhấn ▶ Bắt đầu để xem stream">
    <div class="hint">Stream MJPEG trực tiếp · hộp xanh = người · overlay: số người + FPS</div>
  </div>
</div>
<script>
function startStream(){
  const q = new URLSearchParams({
    src: document.getElementById('video').value,
    model: document.getElementById('model').value,
    conf: document.getElementById('conf').value,
    fisheye: document.getElementById('fisheye').checked ? 1 : 0,
    dispw: document.getElementById('dispw').value,
    t: Date.now()
  });
  document.getElementById('feed').src = `{{ url_for('video_feed') }}?` + q.toString();
}
</script>
</body></html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, videos=list_videos())


@app.route("/video_feed")
def video_feed():
    src   = safe_path(request.args.get("src", ""))
    model = request.args.get("model", DEFAULT_MODEL)
    conf  = float(request.args.get("conf", 0.30))
    fish  = request.args.get("fisheye", "1") == "1"
    dispw = int(request.args.get("dispw", 960))
    det_imgsz = min(960, max(480, (dispw // 32) * 32))
    return Response(
        gen_stream(src, model, fish, conf, k1=-0.30, fs=1.0,
                   det_imgsz=det_imgsz, disp_w=dispw),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f and Path(f.filename).suffix.lower() in VIDEO_EXTS:
        f.save(str(UPLOAD_DIR / Path(f.filename).name))
    return redirect(url_for("index"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()
    print(f"\n→ Mở trình duyệt: http://{args.host}:{args.port}\n", flush=True)
    app.run(host=args.host, port=args.port, threaded=True)
