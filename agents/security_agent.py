"""Security Vulnerability Agent: OWASP-mapped static scan with line-level flagging."""
from agents.base import BaseAgent
from agents.llm_client import llm_review
from agents.security_rules import RULES
from models import Finding

import re


class SecurityVulnerabilityAgent(BaseAgent):
    name = "Security Vulnerability Agent"

    @staticmethod
    def _is_comment(line, lang):
        s = line.strip()
        return s.startswith("#") if lang == "python" else s.startswith(("//", "/*", "*"))

    def analyze(self, sub):
        lines = sub.code.splitlines()
        out = []
        for rule in RULES:
            if sub.language not in rule.langs:
                continue
            if rule.unless_file and re.search(rule.unless_file, sub.code):
                continue
            for i, line in enumerate(lines, 1):
                if self._is_comment(line, sub.language):
                    continue
                if not any(p.search(line) for p in rule.compiled):
                    continue
                if rule.unless and re.search(rule.unless, "\n".join(lines[max(0, i - 4):i + 3]), re.I):
                    continue
                out.append(Finding(self.name, rule.id, rule.title, "Security", rule.severity, i,
                                   rule.description, rule.recommendation, line.strip()[:160],
                                   rule.owasp, rule.cwe))
        if self.use_llm:
            extra, note = llm_review(self.name, "application security (OWASP Top 10)", sub, out)
            self.notes.append(note)
            out += extra
        return out
