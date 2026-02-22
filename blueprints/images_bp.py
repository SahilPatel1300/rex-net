"""
Blueprint: accept text, verify it is text, return an image from imgs/.
"""
import os
from pathlib import Path

from flask import Blueprint, request, send_file, jsonify

images_bp = Blueprint("images", __name__)

# Project root (parent of this package); imgs/ is next to app/
APP_ROOT = Path(__file__).resolve().parent.parent
IMGS_DIR = APP_ROOT / "imgs"

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


def _default_image_path() -> Path | None:
    """Return path to first available image in imgs/ or None."""
    if not IMGS_DIR.is_dir():
        return None
    for p in sorted(IMGS_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS:
            return p
    return None


@images_bp.route("/image", methods=["POST"])
def get_image():
    """
    Expects JSON body: { "text": "<string>", "image": "<optional filename>" }.
    Validates that "text" is valid text; returns image from imgs/ (by name or default).
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    text = data.get("text")
    if not _is_valid_text(text):
        return jsonify({
            "error": "Invalid or missing text. Provide a non-empty string (no path characters)."
        }), 400

    # Optional: specific image filename from imgs/
    image_path = None
    if "image" in data and isinstance(data["image"], str):
        image_path = _safe_image_path(data["image"].strip())

    if image_path is None:
        image_path = _default_image_path()

    if image_path is None:
        return jsonify({
            "error": "No image available. Add a supported image (e.g. .png, .jpg) to the imgs/ folder."
        }), 404

    response = send_file(
        image_path,
        mimetype=None,
        as_attachment=False,
        download_name=image_path.name,
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
