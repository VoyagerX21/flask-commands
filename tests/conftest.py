import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)

if ROOT_STR in sys.path:
    sys.path.remove(ROOT_STR)

sys.path.insert(0, ROOT_STR)