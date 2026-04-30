import io
from PIL import Image


# 保持するEXIFタグのホワイトリスト（何も保持しない = 完全削除）
_SAFE_EXIF_TAGS: set[int] = set()

MAX_DIMENSION = 2048  # 長辺の上限px
WEBP_QUALITY = 85


def process_image(raw_bytes: bytes) -> bytes:
    """
    1. EXIF情報を完全削除
    2. 長辺が MAX_DIMENSION を超える場合はリサイズ
    3. WebP形式に変換・最適化

    Returns:
        WebP形式のバイト列
    """
    with Image.open(io.BytesIO(raw_bytes)) as img:
        # RGBAなどモードを正規化（WebPはRGBA対応だがCMYK等は不可）
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # --- EXIF削除: データをピクセルのみで再構築 ---
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))

        # --- リサイズ（長辺 > MAX_DIMENSION の場合のみ）---
        w, h = clean.size
        if max(w, h) > MAX_DIMENSION:
            ratio = MAX_DIMENSION / max(w, h)
            clean = clean.resize(
                (int(w * ratio), int(h * ratio)),
                Image.LANCZOS,
            )

        # --- WebP変換 ---
        buf = io.BytesIO()
        clean.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        return buf.getvalue()