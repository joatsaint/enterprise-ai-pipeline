"""
Tests for src/utils/atomic.py — atomic file writes.

1. atomic_write_text creates parent dirs, writes content, overwrites cleanly,
   and leaves no temp files behind
2. atomic_write_json round-trips a dict
"""
import json
import os

from src.utils.atomic import atomic_write_text, atomic_write_json


def test_atomic_write_text_creates_and_overwrites(tmp_path):
    p = tmp_path / "sub" / "f.txt"
    atomic_write_text(str(p), "hello")
    assert p.read_text(encoding="utf-8") == "hello"

    atomic_write_text(str(p), "world")
    assert p.read_text(encoding="utf-8") == "world"

    leftovers = [n for n in os.listdir(p.parent) if n.startswith(".tmp_")]
    assert leftovers == []


def test_atomic_write_json_roundtrip(tmp_path):
    p = tmp_path / "state.json"
    obj = {"a": 1, "b": [1, 2, 3], "c": "café"}
    atomic_write_json(str(p), obj)
    assert json.loads(p.read_text(encoding="utf-8")) == obj
