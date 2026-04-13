#!/usr/bin/env python3
"""Backward-compatible entry: delegates to ctqa_pg.py (PuTTY plink-first on Windows)."""

from ctqa_pg import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
