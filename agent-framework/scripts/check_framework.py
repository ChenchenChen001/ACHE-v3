#!/usr/bin/env python3
"""ACHE version 2 configuration and record validator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from framework_validation import check, main

if __name__ == "__main__":
    raise SystemExit(main())
