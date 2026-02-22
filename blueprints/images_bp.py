"""
Blueprint: accept text, verify it is text, run emotion model, return an image from imgs/<emotion>/.
"""
import os
from pathlib import Path

from flask import Blueprint, request, send_file, jsonify

from services.emotion_image import EmotionImageService

images_bp = Blueprint("images", __name__)

# Project root (parent of this package); imgs/ is next to blueprints/
APP_ROOT = Path(__file__).resolve().parent.parent
IMGS_DIR = APP_ROOT / "imgs"

emotion_service = EmotionImageService(imgs_root=IMGS_DIR)

# Allowed image extensions for safe serving
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _is_valid_text(value: object) -> bool:
    """Verify that the value is a non-empty string of reasonable text."""
    if not isinstance(value, str):
        return False
    s = value.strip()
    if not s:
        return False
    # Reject path-like or filename-like input (security)
    if ".." in s or "/" in s or "\\" in s:
        return False
    # Reasonable length (e.g. 100k chars max)
    if len(s) > 100_000:
        return False
    # Optional: ensure it's not obviously binary (high proportion of non-printable)
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _safe_image_path(filename: str) -> Path | None:
    """Return path to image under IMGS_DIR if it exists and is allowed; else None."""
    if not filename or ".." in filename or os.path.sep in filename:
        return None
    base = Path(filename).name
    ext = Path(base).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    path = IMGS_DIR / base
    if not path.is_file():
        return None
    try:
        path.resolve().relative_to(IMGS_DIR.resolve())
    except ValueError:
        return None
    return path


@images_bp.route("/image", methods=["POST"])
def get_image():
    """
    Expects JSON body: { "text": "<string>", "image": "<optional filename>" }.
    Validates text; runs emotion model; returns image from imgs/<emotion>/ (random)
    and analysis in headers. If "image" is provided, serves that file from imgs/ instead.
    """
    print("[images_bp] POST /api/image")
    if not request.is_json:
        print("[images_bp] 415: not JSON")
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True)
    if data is None:
        print("[images_bp] 400: invalid JSON")
        return jsonify({"error": "Invalid JSON body"}), 400

    text = data.get("text")
    if not _is_valid_text(text):
        print("[images_bp] 400: invalid text")
        return jsonify({
            "error": "Invalid or missing text. Provide a non-empty string (no path characters)."
        }), 400

    image_path = None
    analysis = None

    if "image" in data and isinstance(data["image"], str):
        image_path = _safe_image_path(data["image"].strip())
        if image_path:
            print(f"[images_bp] using explicit image: {image_path.name}")

    if image_path is None:
        print("[images_bp] calling emotion_service.get_image_for_text")
        analysis, image_path = emotion_service.get_image_for_text(text)

    if image_path is None:
        label = (analysis or {}).get("label", "unknown")
        print(f"[images_bp] 404: no image for emotion {label}")
        return jsonify({
            "error": f"No image found for this emotion. Add images to imgs/{label}/."
        }), 404

    print(f"[images_bp] 200: sending {image_path.name}" + (f" (emotion={analysis['label']})" if analysis else ""))
    response = send_file(
        image_path,
        mimetype=None,
        as_attachment=False,
        download_name=image_path.name,
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    if analysis is not None:
        response.headers["X-Emotion"] = analysis["label"]
        response.headers["X-Emotion-Score"] = str(analysis["score"])
    return response
