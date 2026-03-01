"""
Condense long text to a random sample of sentences that fits within the model's max token length.
"""
import re
import random
from typing import Optional

# Same model as emotion pipeline so tokenizer matches
DEFAULT_MODEL_ID = "SamLowe/roberta-base-go_emotions"


class TextCondensor:
    """
    Holds raw text and provides get_condensed(max_tokens=512) that returns a string
    of at most max_tokens tokens, built from randomly sampled sentences.
    """

    def __init__(self, text: str, tokenizer=None):
        self.text = (text or "").strip()
        self._tokenizer = tokenizer
        self._model_id = DEFAULT_MODEL_ID

    def _get_tokenizer(self):
        if self._tokenizer is None:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_id)
        return self._tokenizer

    def _split_sentences(self) -> list[str]:
        """Split text on sentence boundaries (. ! ?)."""
        if not self.text:
            return []
        # Split after . ! ? when followed by space or end
        parts = re.split(r"(?<=[.!?])\s+", self.text)
        print(f"parts: {parts}")
        return [p.strip() for p in parts if p.strip()]

    def _count_tokens(self, s: str) -> int:
        tok = self._get_tokenizer()
        return len(tok.encode(s, add_special_tokens=False))

    def get_condensed(self, max_tokens: int = 512) -> str:
        """
        Return a string of at most max_tokens tokens, built from randomly sampled
        sentences. If the text is already short enough, return it as-is (trimmed).
        """
        if not self.text:
            return ""

        sentences = self._split_sentences()
        print(f"sentences: {sentences}")

        if not sentences:
            # No sentence boundaries: treat whole text as one chunk and truncate
            if self._count_tokens(self.text) <= max_tokens:
                return self.text
            tok = self._get_tokenizer()
            ids = tok.encode(self.text, truncation=True, max_length=max_tokens)
            return tok.decode(ids, skip_special_tokens=True)

        # Shuffle so we get a random sample each time
        shuffled = sentences.copy()
        random.shuffle(shuffled)

        chosen: list[str] = []
        used = 0
        for s in shuffled:
            n = self._count_tokens(s)
            if n > max_tokens:
                # Single sentence too long: truncate and use as the only content
                tok = self._get_tokenizer()
                ids = tok.encode(s, truncation=True, max_length=max_tokens)
                return tok.decode(ids, skip_special_tokens=True)
            if used + n > max_tokens:
                break
            chosen.append(s)
            used += n

        return " ".join(chosen) if chosen else self.text[:100]
