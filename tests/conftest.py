# tests/conftest.py
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[1])  # .../video-trust
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)