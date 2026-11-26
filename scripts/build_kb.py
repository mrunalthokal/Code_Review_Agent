"""Run:  python -m scripts.build_kb   [--local]"""
import sys
from rag.pipeline import build_index

if __name__ == "__main__":
    print(build_index(force_local="--local" in sys.argv))
