#!/usr/bin/env bash
# PostToolUse hook: runs the pytest suite when Claude edits a Python file,
# so regressions are caught immediately instead of waiting for CI on PR.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
file_path=$(python -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path') or d.get('tool_response',{}).get('filePath',''))")

case "$file_path" in
  *.py)
    cd "$DIR" || exit 0
    echo "[test-on-edit] $file_path changed — running pytest suite..."
    PYTHONIOENCODING=utf-8 python -m pytest tests/ -q --no-header 2>&1 | tail -8
    ;;
esac
