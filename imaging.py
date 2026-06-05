"""업로드 파일(이미지 또는 PDF)을 비전 모델에 넣을 PNG 바이트로 변환."""

from __future__ import annotations

import io

import fitz  # PyMuPDF
from PIL import Image


def to_png_pages(file_bytes: bytes, filename: str) -> list[bytes]:
    """파일을 PNG 바이트 리스트로 변환.

    - 이미지: 1장 리스트
    - PDF: 페이지 수만큼 리스트(각 페이지를 렌더링)
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _pdf_to_pngs(file_bytes)
    return [_normalize_image(file_bytes)]


def _normalize_image(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _pdf_to_pngs(pdf_bytes: bytes, dpi: int = 200) -> list[bytes]:
    pages: list[bytes] = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        pages.append(pix.tobytes("png"))
    doc.close()
    return pages
