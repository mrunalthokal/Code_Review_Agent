"""Run:  python -m tests.test_milestone2   (or pytest)"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.orchestrator import run_review  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "sample_code"


def sub(name, lang):
    return SimpleNamespace(filename=name, language=lang, code=(ROOT / name).read_text())


def titles(res):
    return {f.title for f in res.findings}


def test_python_sample():
    res = run_review(sub("vulnerable.py", "python"))
    assert "SQL Injection" in titles(res) and "Hardcoded Secret" in titles(res)
    assert res.findings[0].severity.value == "Critical"      # sorted by severity


def test_python_smelly_both_agents():
    res = run_review(sub("smelly.py", "python"))
    t = titles(res)
    for expected in ["Too Many Parameters", "Bare except", "Mutable default argument", "Deep Nesting",
                     "OS Command Injection", "Dangerous eval/exec", "Hardcoded Secret",
                     "Possible Missing Authorization (IDOR)", "Unused import"]:
        assert expected in t, expected
    agents = {f.agent for f in res.findings}
    assert len(agents) == 2                                   # merged from both agents
    assert all(f.id for f in res.findings) and res.summary["total"] == len(res.findings)


def test_java_security_rules():
    res = run_review(sub("Smelly.java", "java"))
    t = titles(res)
    for expected in ["Hardcoded Secret", "Weak Hash Algorithm", "Path Traversal", "Insecure Deserialization"]:
        assert expected in t, expected
    res = run_review(sub("Vulnerable.java", "java"))
    assert "SQL Injection" in titles(res)


def test_agent_failure_isolated():
    bad = SimpleNamespace(filename="x", language="python", code=None)
    res = run_review(bad)
    assert all(r["status"] == "failed" for r in res.agent_runs.values())


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
