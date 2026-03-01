"""
Service: text -> RoBERTa Go Emotions -> top emotion -> random image from imgs/<emotion>/.
"""
import random
from pathlib import Path

# Same 28 labels as utils/make_imgs_dir.py (allowed folder names only)
EMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral",
]

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

DEFAULT_MODEL_ID = "SamLowe/roberta-base-go_emotions"


class EmotionImageService:
    """
    Takes text, runs RoBERTa Go Emotions, maps top emotion to imgs/<emotion>/,
    returns a random image from that folder. Basic error handling with fallbacks.
    Returns neutral image if no image could be found.
    """

    def __init__(
        self,
        imgs_root: Path | None = None,
        model_id: str = DEFAULT_MODEL_ID,
    ) -> None:
        if imgs_root is None:
            imgs_root = Path(__file__).resolve().parent.parent / "imgs"
        self._imgs_root = Path(imgs_root)
        self._model_id = model_id
        self._pipeline = None
        print(f"[EmotionImageService] init imgs_root={self._imgs_root} model_id={self._model_id}")

    def _get_pipeline(self):
        if self._pipeline is None:
            print(f"[EmotionImageService] loading pipeline {self._model_id}...")
            from transformers import pipeline
            self._pipeline = pipeline(
                task="text-classification",
                model=self._model_id,
                top_k=None,
            )
            print("[EmotionImageService] pipeline loaded")
        return self._pipeline

    def _top_emotion(self, text: str) -> tuple[str, float]:
        """Run model, return (label, score) for highest-scoring emotion."""
        print(f"[EmotionImageService] _top_emotion input: {text[:80]!r}...")
        try:
            outputs = self._get_pipeline()([text])
        except Exception as e:
            print(f"[EmotionImageService] pipeline error: {e}")
            return ("neutral", 0.0)
        if not outputs or not outputs[0]:
            print("[EmotionImageService] empty pipeline output, using neutral")
            return ("neutral", 0.0)
        labels_scores = outputs[0]
        best = max(labels_scores, key=lambda x: x["score"])
        label = (best.get("label") or "neutral").strip().lower()
        if label not in EMOTION_LABELS:
            label = "neutral"
        score = float(best.get("score", 0.0))
        print(f"[EmotionImageService] top emotion: {label} (score={score})")
        return (label, score)

    def _images_in_folder(self, folder: Path) -> list[Path]:
        if not folder.is_dir():
            return []
        out = [
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
        ]
        return out

    def _random_image_for_emotion(self, emotion: str) -> Path | None:
        folder = self._imgs_root / emotion
        candidates = self._images_in_folder(folder)
        if candidates:
            chosen = random.choice(candidates)
            print(f"[EmotionImageService] picked image from {emotion}/: {chosen.name}")
            return chosen
        print(f"[EmotionImageService] no images in {emotion}/")
        return None

    def get_image_for_text(self, text: str) -> tuple[dict, Path | None]:
        """
        Returns (analysis, image_path). analysis = {"label": str, "score": float}.
        image_path is None if no image could be found (with fallbacks).
        """
        print(f"[EmotionImageService] get_image_for_text: {text[:60]!r}...")
        if not self._imgs_root.is_dir():
            print("[EmotionImageService] imgs_root is not a directory, returning None")
            return ({"label": "neutral", "score": 0.0}, None)

        label, score = self._top_emotion(text)
        analysis = {"label": label, "score": score}

        path = self._random_image_for_emotion(label)
        if path is not None:
            print(f"[EmotionImageService] returning image for emotion {label}")
            return (analysis, path)

        print(f"[EmotionImageService] fallback: trying neutral/")
        path = self._random_image_for_emotion("neutral")
        if path is not None:
            print("[EmotionImageService] returning image from neutral/")
            return (analysis, path)

        print("[EmotionImageService] fallback: trying other emotion folders")
        for other in EMOTION_LABELS:
            if other == label or other == "neutral":
                continue
            path = self._random_image_for_emotion(other)
            if path is not None:
                print(f"[EmotionImageService] returning image from {other}/")
                return (analysis, path)

        print("[EmotionImageService] no image found anywhere, returning None")
        return (analysis, None)
