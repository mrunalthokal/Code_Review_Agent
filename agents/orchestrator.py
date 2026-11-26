"""Multi-agent orchestration: run agents in parallel, merge into one unified findings list."""
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from agents.code_analysis_agent import CodeAnalysisAgent
from agents.security_agent import SecurityVulnerabilityAgent
from models import Severity

PENALTY = {"Critical": 15, "High": 8, "Medium": 4, "Low": 1, "Info": 0}


@dataclass
class ReviewResult:
    filename: str
    language: str
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    agent_runs: dict = field(default_factory=dict)
    total_seconds: float = 0.0

    def to_dict(self):
        return {"filename": self.filename, "language": self.language, "summary": self.summary,
                "agent_runs": self.agent_runs, "total_seconds": self.total_seconds,
                "findings": [f.to_dict() for f in self.findings]}


def _run_agent(agent, sub):
    t0 = time.perf_counter()
    try:
        findings, status, err = agent.analyze(sub), "ok", ""
    except Exception as e:      # one failing agent must not break the other
        findings, status, err = [], "failed", str(e)
    return agent.name, findings, {"status": status, "findings": len(findings),
                                  "seconds": round(time.perf_counter() - t0, 3),
                                  "notes": agent.notes, "error": err}


def _merge(results):
    merged, seen = [], set()
    for f in (f for r in results for f in r):
        key = (f.line, f.title.lower())
        if key not in seen:
            seen.add(key)
            merged.append(f)
    rule_lines = {(f.agent, f.line) for f in merged if f.source == "rule"}
    merged = [f for f in merged if f.source == "rule" or (f.agent, f.line) not in rule_lines]
    merged.sort(key=lambda f: (-f.score, f.line))
    for n, f in enumerate(merged, 1):
        f.id = f"F-{n:03d}"
    return merged


def _summarize(findings):
    by_sev = {s.value: 0 for s in Severity}
    by_agent, by_cat = {}, {}
    for f in findings:
        by_sev[f.severity.value] += 1
        by_agent[f.agent] = by_agent.get(f.agent, 0) + 1
        by_cat[f.category] = by_cat.get(f.category, 0) + 1
    score = max(0, 100 - sum(PENALTY[k] * v for k, v in by_sev.items()))
    return {"total": len(findings), "by_severity": by_sev, "by_agent": by_agent,
            "by_category": by_cat, "health_score": score}


def run_review(sub, use_llm: bool = False) -> ReviewResult:
    agents = [CodeAnalysisAgent(use_llm), SecurityVulnerabilityAgent(use_llm)]
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(agents)) as pool:       # parallel execution
        futures = [pool.submit(_run_agent, a, sub) for a in agents]
        outputs = [f.result() for f in futures]
    findings = _merge([o[1] for o in outputs])
    return ReviewResult(sub.filename, sub.language, findings, _summarize(findings),
                        {o[0]: o[2] for o in outputs}, round(time.perf_counter() - t0, 3))
