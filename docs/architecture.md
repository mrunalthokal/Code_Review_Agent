# Architecture and Design (Milestone 1)

## Flow
Developer -> Code Submission Module (paste / upload, syntax validation) -> Orchestrator (Milestone 3)
-> [Code Analysis Agent | Security Vulnerability Agent] in parallel -> Remediation Agent
-> PR Summary Agent -> Report export.
The Conversational Assistant queries the Secure Coding Knowledge Base (RAG) at any time.

## Agent Responsibilities
| Agent | Responsibility | Milestone |
|---|---|---|
| Code Analysis | Code smells, complexity, anti-patterns | 2-3 |
| Security Vulnerability | OWASP checks: SQLi, XSS, CSRF, secrets, auth | 2-3 |
| Remediation | Fix suggestions with corrected code (uses RAG) | 3 |
| PR Summary | Structured human-readable review | 3-4 |
| Conversational Assistant | RAG Q&A on findings | 4 |

## RAG Pipeline (built in Milestone 1)
Markdown docs -> heading-aware chunking (800 chars, 120 overlap) -> embeddings (Gemini gemini-embedding-001, local fallback) -> ChromaDB (cosine) -> top-k retrieval.

## Data Models
- Submission: filename, language, code, valid, issues[], metrics
- Finding (next milestone): id, agent, category, severity (Critical/High/Medium/Low/Info), line, description, owasp_ref
- Remediation: finding_id, explanation, fixed_code, references[]
- Review: submission, findings[], remediations[], summary, score

## Tech Stack
Python, Streamlit, javalang + ast (syntax validation), ChromaDB, Google Gemini API.

---
# Milestone 2: Agents and Orchestration

## Orchestration flow
Submission -> `run_review()` -> ThreadPoolExecutor runs both agents **in parallel**
-> each returns `list[Finding]` -> merge (dedupe by line+title, sort by severity score, assign F-001...)
-> `ReviewResult` (findings, severity summary, health score, per-agent status/timing).
A failing agent is isolated: the other agent's results are still returned.

## Code Analysis Agent
Python: `ast` (functions, classes, handlers, imports). Java: `javalang` + brace matching.
Checks: long method, too many parameters, cyclomatic complexity, deep nesting, god class, bare/empty/broad catch,
mutable default args, unused imports, wildcard imports, global state, naming, long lines, TODO markers.

## Security Vulnerability Agent
Rule engine (`security_rules.py`, ~35 rules) mapped to OWASP Top 10 2021 + CWE: SQL/command injection, XSS, CSRF,
hardcoded secrets, weak crypto/hash, insecure deserialization, XXE, SSRF, path traversal, access-control and
authentication flaws, debug/misconfiguration. Each finding carries line number, snippet, severity, OWASP, CWE.

## Severity scoring
Critical 9.5 | High 7.5 | Medium 5.0 | Low 2.5 | Info 0.5.
Health score = 100 - (15 x Critical + 8 x High + 4 x Medium + 1 x Low), minimum 0.

## Optional Gemini layer
Each agent can additionally ask Gemini (JSON output, told not to repeat rule findings). Failures never break the run.

---
# Milestone 2, Task 4: Detection Accuracy Validation

- `validation/samples/` holds 6 labeled files: vulnerable, code-smell and clean versions in Python and Java.
- Every known issue is labeled in the file with a comment `EXPECT: <issue title>`. Labels are stripped before analysis.
- `validation/run_validation.py` runs the real agents and compares findings with labels:
  TP (found), FN (missed), FP (not labeled). Precision = TP/(TP+FP), Recall = TP/(TP+FN), F1 = harmonic mean.
- Security findings must match on exact line; quality findings allow +-1 line (they anchor on declarations).
- Clean files test false alarms: safe code (parameterized SQL, secrets module, env vars, PreparedStatement,
  AES/GCM) must produce zero findings.
- Output: `validation/validation_report.md` and `validation_results.json`; also shown in the app's Accuracy Validation tab.
- Validation found a real rule bug (Flask `config["WTF_CSRF_ENABLED"] = False` was missed); the rule was fixed.
- Known limitations (deliberately included as labeled hard cases): SQL strings split over several lines are missed
  because rules inspect one line at a time. Future work: data-flow / taint analysis.
