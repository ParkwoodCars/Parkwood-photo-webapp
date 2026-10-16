
from io import BytesIO
import base64
import json
from pathlib import Path

from PIL import Image, ImageEnhance

from openai import OpenAI

APP_DIR = Path(__file__).resolve().parent
CFG = json.loads((APP_DIR / "config.json").read_text(encoding="utf-8"))
PROMPT = (APP_DIR / "prompt.txt").read_text(encoding="utf-8")

def safe_tone_finish(image):
    tone_cfg = CFG.get("tone_finish", {})
    if not tone_cfg.get("enabled", True):
        return image

    arr = image.convert("L")
    import numpy as np
    lum = np.asarray(arr, dtype=np.float32) / 255.0
    mean_lum = float(lum.mean())
    target = 0.50
    raw = (target / mean_lum) if mean_lum > 0 else 1.0

    max_change = float(tone_cfg.get("max_brightness_change", 0.04))
    brightness = max(1.0 - max_change, min(1.0 + max_change, raw))

    out = ImageEnhance.Brightness(image).enhance(brightness)
    out = ImageEnhance.Contrast(out).enhance(float(tone_cfg.get("contrast", 1.02)))
    out = ImageEnhance.Color(out).enhance(float(tone_cfg.get("colour", 1.02)))
    out = ImageEnhance.Sharpness(out).enhance(float(tone_cfg.get("sharpness", 1.02)))
    return out

def edit_image_bytes(image_bytes, mask_bytes, api_key):
    client = OpenAI(api_key=api_key)

    result = client.images.edit(
        model=CFG["model"],
        image=("image.png", image_bytes, "image/png"),
        mask=("mask.png", mask_bytes, "image/png"),
        prompt=PROMPT,
        n=1,
        output_format=CFG.get("output_format", "jpeg"),
        output_compression=int(CFG.get("output_compression", 94)),
        quality=CFG.get("quality", "high"),
        input_fidelity=CFG.get("input_fidelity", "high"),
    )

    item = result.data[0]
    if getattr(item, "b64_json", None):
        raw = base64.b64decode(item.b64_json)
    elif getattr(item, "url", None):
        import urllib.request
        raw = urllib.request.urlopen(item.url).read()
    else:
        raise RuntimeError("No image data returned by API")

    edited = Image.open(BytesIO(raw)).convert("RGB")
    edited = safe_tone_finish(edited)
    out = BytesIO()
    edited.save(out, format="JPEG", quality=int(CFG.get("output_compression", 94)), subsampling=0)
    return out.getvalue()
