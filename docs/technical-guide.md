# RexNet Backend — Technical Guide

Short overview of how the RexNet backend is built and how it runs.

## Stack

- **Python** — 3.12+
- **Web** — Flask 3.x, flask-cors
- **Model** — Hugging Face `transformers`; RoBERTa-based Go Emotions classifier (`SamLowe/roberta-base-go_emotions`)
- **Runtime** — PyTorch (CPU or CUDA/MPS if available)

See `pyproject.toml` for exact dependency versions.

## Project Layout

```
rexnet/
├── app.py                 # Flask app entry; CORS; registers blueprints
├── blueprints/
│   └── images_bp.py        # POST /api/image — text in, image + emotion out
├── services/
│   └── emotion_image.py    # EmotionImageService: model + imgs/<emotion>/
├── imgs/                   # Per-emotion image folders (e.g. imgs/joy/, imgs/neutral/)
├── utils/
│   └── make_imgs_dir.py    # Creates imgs/ and subfolders for each emotion
└── docs/
    ├── technical-guide.md  # This file
    └── api-guide.md        # API reference
```

## Request Flow

1. Client sends `POST /api/image` with JSON `{ "text": "..." }`.
2. **Blueprint** (`images_bp`) validates body and text (non-empty string, no path chars, length limit).
3. If no explicit `"image"` filename is given, **EmotionImageService** is used:
   - **Model** — Lazy-loaded Hugging Face `text-classification` pipeline (RoBERTa Go Emotions, `top_k=None`). First request triggers download/load; later requests reuse the same pipeline.
   - **Analysis** — Pipeline returns scores for 28 emotions; the service picks the **top-scoring label**.
   - **Image** — Service looks in `imgs/<label>/` (e.g. `imgs/joy/`), picks a **random** image (`.png`, `.jpg`, etc.). If that folder is missing or empty, it tries `imgs/neutral/`, then any other emotion folder.
4. Response is the **image bytes** with optional headers `X-Emotion` and `X-Emotion-Score`. On error (invalid input, no image found), the API returns JSON with an `error` message and an appropriate status code.

## Model

- **Source** — `SamLowe/roberta-base-go_emotions` on the Hugging Face Hub.
- **Task** — Multi-label text classification over 28 Go Emotions labels (admiration, amusement, anger, …, neutral).
- **Usage** — We take the single **highest-scoring** label to choose the folder under `imgs/`. The pipeline is created once per process (lazy on first request) and kept in memory.

## Image Directory

- **Layout** — `imgs/<emotion>/` with one folder per emotion (e.g. `imgs/joy/`, `imgs/sadness/`). Run `utils/make_imgs_dir.py` to create the structure.
- **Allowed extensions** — `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`.
- **Security** — Only filenames under these emotion folders are served; no path traversal (e.g. `..` or `/`) is allowed.

## CORS

CORS is enabled for the whole app via `flask_cors.CORS(app)`, so all routes (including error responses) send the usual CORS headers and preflight `OPTIONS` requests are handled. The extension or any web client can call the API from another origin.

## Running the Server

From the project root:

```bash
uv sync          # or: pip install -e .
python app.py
```

Server listens on `http://localhost:5000` by default. Change host/port in `app.py` if needed.

## Environment

No required env vars for basic run. Optional future use: model path, `imgs` path, API key, or debug flags can be read from the environment and passed into the app or `EmotionImageService`.
