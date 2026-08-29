"""
Atomic file writes — never leave a half-written state file.

Why: a crash or power loss mid-write (a real risk here — see the power-outage
state-corruption history) can leave a JSON state file truncated and unparseable.
These helpers write to a temp file in the same directory, fsync it, then
os.replace() it onto the target. os.replace is atomic on the same filesystem
(Windows and POSIX), so a reader always sees either the old complete file or the
new complete file — never a torn half-file.

Use for any state/log/JSON the pipeline mutates (e.g. dashboard_state.json).
"""
import json
import os
import tempfile


def atomic_write_text(path, text, encoding="utf-8"):
    """Write text to path atomically (temp file -> fsync -> os.replace)."""
    path = str(path)
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp_", suffix=".swap")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)  # atomic swap on the same filesystem
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_json(path, obj, indent=2):
    """Serialize obj to JSON and write it to path atomically."""
    atomic_write_text(path, json.dumps(obj, indent=indent, ensure_ascii=False))
