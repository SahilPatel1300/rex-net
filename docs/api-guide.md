# RexNet Backend — API Guide

Base URL (default): `http://localhost:5000`

All API responses that are JSON use a single key `error` for error messages. Success responses for the image endpoint return the image bytes with optional headers.

---

## POST /api/image

Send text; receive an image chosen by the emotion model (or an explicit image by filename), plus emotion metadata in headers.

### Request

- **Method:** `POST`
- **URL:** `/api/image`
- **Content-Type:** `application/json`
- **Body (JSON):**

| Field   | Type   | Required | Description |
|--------|--------|----------|-------------|
| `text` | string | Yes      | Input text to analyze. Must be non-empty, no `..` / `/` / `\`, max length 100,000 characters, valid UTF-8. |
| `image`| string | No       | If provided, serve this file from the root of `imgs/` (e.g. `"image": "default.png"`). Skips the emotion model. |

**Example (emotion-based image):**

```json
{
  "text": "I am so happy today!"
}
```

**Example (explicit image file):**

```json
{
  "text": "any valid text",
  "image": "pixel-art-brachiosaurus.png"
}
```

### Success Response (200)

- **Body:** Image bytes (e.g. PNG/JPEG).
- **Headers:**
  - `Content-Type` — Inferred from file (e.g. `image/png`).
  - `X-Emotion` — Top emotion label (e.g. `joy`, `sadness`). Present only when the emotion model was used (no `image` in request).
  - `X-Emotion-Score` — Model score for that label (0–1). Present only when the emotion model was used.

**Example (curl):**

```bash
curl -X POST http://localhost:5000/api/image \
  -H "Content-Type: application/json" \
  -d '{"text": "I am not having a great day"}' \
  --output out.png
```

**Example (JavaScript):**

```javascript
const res = await fetch('http://localhost:5000/api/image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'I am so happy today!' }),
});

if (!res.ok) {
  const err = await res.json();
  console.error(err.error);
  return;
}

const blob = await res.blob();
const emotion = res.headers.get('X-Emotion');
const score = res.headers.get('X-Emotion-Score');
// e.g. use blob for <img src={URL.createObjectURL(blob)} />
```

### Error Responses

| Status | Condition | Body (JSON) |
|--------|-----------|-------------|
| **400** | Missing or invalid JSON | `{"error": "Invalid JSON body"}` |
| **400** | Invalid or missing `text` (empty, path chars, too long, etc.) | `{"error": "Invalid or missing text. Provide a non-empty string (no path characters)."}` |
| **404** | No image found for the predicted emotion (and fallbacks) | `{"error": "No image found for this emotion. Add images to imgs/<label>/."}` |
| **415** | Request body is not JSON | `{"error": "Content-Type must be application/json"}` |

**Example (error):**

```bash
curl -X POST http://localhost:5000/api/image \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'
# 400, {"error": "Invalid or missing text. ..."}
```

### Emotion Labels

The model uses the Go Emotions label set. The value in `X-Emotion` is one of:

admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral.

Image folders under `imgs/` are named with these labels (e.g. `imgs/joy/`, `imgs/neutral/`).
