"""Tiny dependency-free keyword retrieval over markdown/text files."""
from __future__ import annotations

import os
import re
from collections import Counter

DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


def load_chunks(directory: str = DEFAULT_DIR) -> list[str]:
    chunks = []
    for name in sorted(os.listdir(directory)):
        if name.endswith((".md", ".txt")):
            with open(os.path.join(directory, name), encoding="utf-8") as f:
                chunks += [c.strip() for c in re.split(r"\n\s*\n", f.read()) if c.strip()]
    return chunks


def search(query: str, k: int = 3, directory: str = DEFAULT_DIR) -> list[str]:
    q = Counter(_tokens(query))
    scored = []
    for c in load_chunks(directory):
        t = Counter(_tokens(c))
        score = sum(min(t[w], 3) for w in q if w in t)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]
