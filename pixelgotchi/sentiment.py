from typing import Tuple

# Simple, fast sentiment approximation without external libs.
# Returns sentiment in [-1, 1] and a label.

POS_WORDS = {
    "love","like","yay","good","great","happy","fun","nice","awesome","cool","enjoy",
    "cute","sweet","bravo","wow","woo","thanks","thank you","yummy","delicious","delish"
}
NEG_WORDS = {
    "sad","angry","mad","hate","bad","terrible","awful","boring","tired","exhausted","dirty",
    "ew","eww","yuck","hungry","starving","lonely","cry","upset","ugh","grr"
}


def sentiment_score(text: str) -> Tuple[float, str]:
    t = text.lower()
    pos = sum(1 for w in POS_WORDS if w in t)
    neg = sum(1 for w in NEG_WORDS if w in t)
    if pos == 0 and neg == 0:
        return 0.0, "neutral"
    score = (pos - neg) / max(1, pos + neg)
    label = "positive" if score > 0 else ("negative" if score < 0 else "neutral")
    return max(-1.0, min(1.0, score)), label
