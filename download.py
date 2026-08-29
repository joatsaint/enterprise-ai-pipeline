"""
Entry point preserved for backwards compatibility.
All logic is handled by src/orchestrator.py.
"""
import sys
from src.orchestrator import run


def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <YouTube URL>")
        sys.exit(1)
    run(sys.argv[1])


if __name__ == "__main__":
    main()
