from transformers import pipeline

_pipe = None

def get_pipe():
    global _pipe
    if _pipe is None:
        # "t5-small" is enough for CPU, ~240MB
        _pipe = pipeline("summarization", model="t5-small")
    return _pipe

def summarize_t5(text_in: str, max_new_tokens: int = 100) -> str:
    pipe = get_pipe()
    # truncate input for safety (t5-small max length ≈ 512 tokens)
    text = text_in[:2000]
    out = pipe(
        text,
        max_new_tokens=max_new_tokens,
        num_beams=2,
        no_repeat_ngram_size=3,
    )[0]["summary_text"]
    return out
