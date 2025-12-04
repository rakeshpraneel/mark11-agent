import re
from typing import List

def simple_chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Naive chunker: split on sentences then accumulate until chunk_size (~ chars)
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) <= chunk_size:
            cur = (cur + " " + s).strip()
        else:
            if cur:
                chunks.append(cur)
            cur = s
    if cur:
        chunks.append(cur)
    # Add overlap if needed (simple approach)
    out = []
    for c in chunks:
        out.append(c)
    return out
