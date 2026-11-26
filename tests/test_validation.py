"""Run:  python -m tests.test_validation"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validation.run_validation import run_validation  # noqa: E402


def test_accuracy_thresholds():
    r = run_validation(False)
    total = next(m for m in r["metrics"] if m["language"] == "all" and m["agent"] == "all")
    assert total["precision"] >= 0.90, total      # few false alarms
    assert total["recall"] >= 0.90, total         # most known issues found


def test_clean_files_have_no_findings():
    r = run_validation(False)
    clean = [f for f in r["files"] if "Clean" in f["file"] or "clean" in f["file"]]
    assert clean and all(f["found"] == 0 for f in clean), clean


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
