"""Detection-accuracy validation (Milestone 2, task 4).

Every sample file in validation/samples/ marks its KNOWN issues with a comment:
    <code>   # EXPECT: SQL Injection | Hardcoded Secret      (Java: // EXPECT: ...)
The label comments are stripped before analysis (line numbers stay the same), the real
agents run, and findings are compared with the labels:
    TP = expected issue found   FN = expected issue missed   FP = finding that was not expected
Run:  python -m validation.run_validation            (static rules only, reproducible)
      python -m validation.run_validation --llm      (include Gemini findings)
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.orchestrator import run_review          # noqa: E402
from agents.security_rules import RULES              # noqa: E402

SAMPLES = Path(__file__).parent / "samples"
LANG = {".py": "python", ".java": "java"}
EXPECT = re.compile(r"(?:#|//)\s*EXPECT:\s*(.+?)\s*$")
SECURITY, QUALITY = "Security Vulnerability Agent", "Code Analysis Agent"
SECURITY_TITLES = {r.title for r in RULES}
LINE_TOLERANCE = {SECURITY: 0, QUALITY: 1}   # quality findings anchor on a declaration line (+-1)


def agent_of(title):
    return SECURITY if title in SECURITY_TITLES else QUALITY


def load_expected(raw):
    out = []
    for n, line in enumerate(raw.splitlines(), 1):
        m = EXPECT.search(line)
        if m:
            out += [(n, t.strip()) for t in m.group(1).split("|") if t.strip()]
    return out


def strip_labels(raw):
    return "\n".join(EXPECT.sub("", l).rstrip() for l in raw.splitlines())


def match(expected, findings):
    tp, fn, pool = [], [], list(findings)
    for line, title in expected:
        tol = LINE_TOLERANCE[agent_of(title)]
        hit = next((f for f in pool if f.title == title and abs(f.line - line) <= tol), None)
        if hit:
            tp.append((line, title))
            pool.remove(hit)
        else:
            fn.append((line, title))
    fp = [(f.line, f.title, f.agent) for f in pool]
    return tp, fn, fp


def _ratio(a, b):
    return round(a / b, 3) if b else None


def prf(c):
    p, r = _ratio(c["tp"], c["tp"] + c["fp"]), _ratio(c["tp"], c["tp"] + c["fn"])
    f1 = round(2 * p * r / (p + r), 3) if p and r else (0.0 if p is not None and r is not None else None)
    return {**c, "precision": p, "recall": r, "f1": f1}


def run_validation(use_llm=False):
    counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    by_title = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    files, missed, false_pos, warnings = [], [], [], []

    for path in sorted(SAMPLES.iterdir()):
        if path.suffix not in LANG:
            continue
        lang, raw = LANG[path.suffix], path.read_text(encoding="utf-8")
        expected = load_expected(raw)
        res = run_review(SimpleNamespace(filename=path.name, language=lang, code=strip_labels(raw)), use_llm)
        failed = {a for a, r in res.agent_runs.items() if r["status"] == "failed"}
        for a in failed:
            warnings.append(f"{path.name}: {a} failed ({res.agent_runs[a]['error'][:80]}), its labels were skipped")
        expected = [e for e in expected if agent_of(e[1]) not in failed]
        tp, fn, fp = match(expected, res.findings)
        files.append({"file": path.name, "language": lang, "expected": len(expected),
                      "found": len(res.findings), "tp": len(tp), "fn": len(fn), "fp": len(fp)})
        for line, title in tp:
            for key in ((lang, agent_of(title)), ("all", agent_of(title)), ("all", "all")):
                counts[key]["tp"] += 1
            by_title[title]["tp"] += 1
        for line, title in fn:
            for key in ((lang, agent_of(title)), ("all", agent_of(title)), ("all", "all")):
                counts[key]["fn"] += 1
            by_title[title]["fn"] += 1
            missed.append({"file": path.name, "line": line, "title": title})
        for line, title, agent in fp:
            for key in ((lang, agent), ("all", agent), ("all", "all")):
                counts[key]["fp"] += 1
            by_title[title]["fp"] += 1
            false_pos.append({"file": path.name, "line": line, "title": title, "agent": agent})

    rows = [{"language": k[0], "agent": k[1], **prf(v)} for k, v in sorted(counts.items())]
    titles = [{"title": t, **prf(v)} for t, v in sorted(by_title.items(), key=lambda kv: kv[0])]
    return {"files": files, "metrics": rows, "by_title": titles, "missed": missed,
            "false_positives": false_pos, "warnings": warnings, "used_llm": use_llm}


def _pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def to_markdown(r):
    L = ["# Detection Accuracy Validation Report", "",
         "Method: sample files with known, labeled issues are analysed by the real agents "
         f"({'static rules + Gemini' if r['used_llm'] else 'static rules only'}). "
         "TP = known issue found, FN = known issue missed, FP = finding not in the labels.", ""]
    if r["warnings"]:
        L += ["**Warnings**", ""] + [f"- {w}" for w in r["warnings"]] + [""]
    L += ["## Overall and per-agent accuracy", "", "| Scope | Agent | TP | FP | FN | Precision | Recall | F1 |",
          "|---|---|---|---|---|---|---|---|"]
    for m in r["metrics"]:
        L.append(f"| {m['language']} | {m['agent']} | {m['tp']} | {m['fp']} | {m['fn']} | "
                 f"{_pct(m['precision'])} | {_pct(m['recall'])} | {_pct(m['f1'])} |")
    L += ["", "## Per file", "", "| File | Language | Known issues | Findings | TP | FP | FN |", "|---|---|---|---|---|---|---|"]
    for f in r["files"]:
        L.append(f"| {f['file']} | {f['language']} | {f['expected']} | {f['found']} | {f['tp']} | {f['fp']} | {f['fn']} |")
    L += ["", "## Per issue type", "", "| Issue | TP | FP | FN | Precision | Recall |", "|---|---|---|---|---|---|"]
    for t in r["by_title"]:
        L.append(f"| {t['title']} | {t['tp']} | {t['fp']} | {t['fn']} | {_pct(t['precision'])} | {_pct(t['recall'])} |")
    L += ["", "## Missed issues (false negatives)", ""]
    L += [f"- {m['file']} line {m['line']}: {m['title']}" for m in r["missed"]] or ["- none"]
    L += ["", "## False alarms (false positives)", ""]
    L += [f"- {f['file']} line {f['line']}: {f['title']} ({f['agent']})" for f in r["false_positives"]] or ["- none"]
    return "\n".join(L) + "\n"


def main():
    r = run_validation(use_llm="--llm" in sys.argv)
    out = Path(__file__).parent
    (out / "validation_results.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    md = to_markdown(r)
    (out / "validation_report.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
