
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

APP_DIR = Path(__file__).resolve().parent
CFG = json.loads((APP_DIR / "config.json").read_text(encoding="utf-8"))

_YOLO = None

def _get_yolo():
    global _YOLO
    if _YOLO is not None:
        return _YOLO
    if YOLO is None:
        return None
    for name in ["yolo11n-seg.pt", "yolov8n-seg.pt"]:
        try:
            _YOLO = YOLO(name)
            return _YOLO
        except Exception:
            continue
    return None

def pil_open(uploaded_file):
    return Image.open(uploaded_file).convert("RGB")

def vehicle_protection_mask(image, padding_px=None):
    padding_px = int(CFG["vehicle_mask_padding_px"] if padding_px is None else padding_px)
    h, w = image.height, image.width
    protect = np.zeros((h, w), dtype=np.uint8)
    model = _get_yolo()
    if model is None:
        return protect

    try:
        result = model.predict(np.array(image), verbose=False, conf=0.20, imgsz=960)[0]
        if result.masks is None or result.boxes is None:
            return protect
        names = result.names
        wanted = {"car", "truck", "bus", "motorcycle", "person", "bicycle"}
        masks = result.masks.data.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)

        for m, c in zip(masks, classes):
            name = names.get(int(c), str(c))
            if name not in wanted:
                continue
            mm = Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
            arr = np.array(mm)
            protect = np.maximum(protect, arr)

        if padding_px > 0:
            k = padding_px * 2 + 1
            if k % 2 == 0:
                k += 1
            protect = np.array(Image.fromarray(protect).filter(ImageFilter.MaxFilter(k)))
    except Exception:
        return np.zeros((h, w), dtype=np.uint8)

    return protect

def make_edit_mask(image, floor_start_ratio=None, padding_px=None, feather_px=None):
    floor_start_ratio = float(CFG["floor_start_ratio"] if floor_start_ratio is None else floor_start_ratio)
    padding_px = int(CFG["vehicle_mask_padding_px"] if padding_px is None else padding_px)
    feather_px = int(CFG["mask_feather_px"] if feather_px is None else feather_px)

    w, h = image.size
    alpha = np.full((h, w), 255, dtype=np.uint8)
    y0 = max(0, min(h-1, int(h * floor_start_ratio)))
    alpha[y0:, :] = 0

    protect = vehicle_protection_mask(image, padding_px=padding_px)
    alpha[protect > 60] = 255

    edge = max(6, int(min(w, h) * 0.008))
    alpha[:edge, :] = 255
    alpha[-edge:, :] = 255
    alpha[:, :edge] = 255
    alpha[:, -edge:] = 255

    mask = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    mask.putalpha(Image.fromarray(alpha))

    if feather_px > 0:
        blurred = mask.getchannel("A").filter(ImageFilter.GaussianBlur(feather_px))
        a = np.array(blurred)
        a[alpha >= 250] = 255
        mask.putalpha(Image.fromarray(a.astype(np.uint8)))

    return mask

def mask_preview(original, mask):
    img = original.convert("RGBA")
    a = np.array(mask.getchannel("A"))
    overlay = Image.new("RGBA", original.size, (255, 70, 70, 0))
    oa = np.zeros_like(a)
    oa[a < 128] = 95
    overlay.putalpha(Image.fromarray(oa))
    return Image.alpha_composite(img, overlay).convert("RGB")

def to_png_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def to_jpeg_bytes(img, quality=92):
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, subsampling=0)
    return buf.getvalue()
