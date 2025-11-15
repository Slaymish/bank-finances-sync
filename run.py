#!/usr/bin/env python3
"""Entry point for running the bank sync service."""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from bank_sync.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
