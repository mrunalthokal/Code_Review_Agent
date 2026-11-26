"""Shared data models used by every agent and the orchestrator."""
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

    @classmethod
    def parse(cls, text, default=None):
        for s in cls:
            if s.value.lower() == str(text).strip().lower():
                return s
        return default or cls.LOW


SEVERITY_SCORE = {Severity.CRITICAL: 9.5, Severity.HIGH: 7.5, Severity.MEDIUM: 5.0,
                  Severity.LOW: 2.5, Severity.INFO: 0.5}
SEVERITY_ICON = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵", "Info": "⚪"}


@dataclass
class Finding:
    agent: str
    rule_id: str
    title: str
    category: str          # e.g. "Complexity" or "Injection"
    severity: Severity
    line: int
    description: str
    recommendation: str = ""
    snippet: str = ""
    owasp: str = ""        # e.g. "A03:2021 Injection"
    cwe: str = ""          # e.g. "CWE-89"
    source: str = "rule"   # "rule" (static) or "llm" (Gemini)
    id: str = ""

    @property
    def score(self) -> float:
        return SEVERITY_SCORE[self.severity]

    def to_dict(self):
        d = asdict(self)
        d["severity"] = self.severity.value
        d["score"] = self.score
        return d
