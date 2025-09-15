import re

def summarize_rule_based(text_in: str, max_sentences: int = 3) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text_in) if s.strip()]
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # simple scoring: prefer near ~18 words, slight bias to earlier sentences
    def score(i, s):
        length = len(s.split())
        return -abs(length - 18) - i * 0.2

    ranked = sorted([(i, s, score(i, s)) for i, s in enumerate(sentences)],
                    key=lambda t: t[2], reverse=True)[:max_sentences]
    keep = [s for i, s, _ in sorted(ranked, key=lambda t: t[0])]
    return " ".join(keep)
