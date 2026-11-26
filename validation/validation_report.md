# Detection Accuracy Validation Report

Method: sample files with known, labeled issues are analysed by the real agents (static rules only). TP = known issue found, FN = known issue missed, FP = finding not in the labels.

**Warnings**

- JavaClean.java: Code Analysis Agent failed (No module named 'javalang'), its labels were skipped
- JavaCodeSmells.java: Code Analysis Agent failed (No module named 'javalang'), its labels were skipped
- JavaVulnerable.java: Code Analysis Agent failed (No module named 'javalang'), its labels were skipped

## Overall and per-agent accuracy

| Scope | Agent | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| all | Code Analysis Agent | 15 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| all | Security Vulnerability Agent | 40 | 0 | 2 | 100.0% | 95.2% | 97.5% |
| all | all | 55 | 0 | 2 | 100.0% | 96.5% | 98.2% |
| java | Security Vulnerability Agent | 17 | 0 | 1 | 100.0% | 94.4% | 97.1% |
| python | Code Analysis Agent | 15 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| python | Security Vulnerability Agent | 23 | 0 | 1 | 100.0% | 95.8% | 97.9% |

## Per file

| File | Language | Known issues | Findings | TP | FP | FN |
|---|---|---|---|---|---|---|
| JavaClean.java | java | 0 | 0 | 0 | 0 | 0 |
| JavaCodeSmells.java | java | 0 | 0 | 0 | 0 | 0 |
| JavaVulnerable.java | java | 18 | 17 | 17 | 0 | 1 |
| py_clean.py | python | 0 | 0 | 0 | 0 | 0 |
| py_code_smells.py | python | 15 | 15 | 15 | 0 | 0 |
| py_vulnerable_web.py | python | 24 | 23 | 23 | 0 | 1 |

## Per issue type

| Issue | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|
| Bare except | 1 | 0 | 0 | 100.0% | 100.0% |
| Binds to All Interfaces | 1 | 0 | 0 | 100.0% | 100.0% |
| CSRF Protection Disabled | 2 | 0 | 0 | 100.0% | 100.0% |
| Cross-Site Scripting (XSS) | 2 | 0 | 0 | 100.0% | 100.0% |
| Dangerous eval/exec | 1 | 0 | 0 | 100.0% | 100.0% |
| Debug Mode Enabled | 1 | 0 | 0 | 100.0% | 100.0% |
| Deep Nesting | 1 | 0 | 0 | 100.0% | 100.0% |
| Exposed Cloud Key / Private Key | 2 | 0 | 0 | 100.0% | 100.0% |
| Hardcoded Secret | 2 | 0 | 0 | 100.0% | 100.0% |
| High Cyclomatic Complexity | 1 | 0 | 0 | 100.0% | 100.0% |
| Information Exposure via Stack Trace | 1 | 0 | 0 | 100.0% | 100.0% |
| Insecure Authentication | 2 | 0 | 0 | 100.0% | 100.0% |
| Insecure Deserialization | 3 | 0 | 0 | 100.0% | 100.0% |
| Insecure Randomness | 2 | 0 | 0 | 100.0% | 100.0% |
| Insecure Temp File | 1 | 0 | 0 | 100.0% | 100.0% |
| Large Class (God Class) | 1 | 0 | 0 | 100.0% | 100.0% |
| Long Method | 1 | 0 | 0 | 100.0% | 100.0% |
| Missing / Client-Controlled Access Check | 1 | 0 | 0 | 100.0% | 100.0% |
| Missing docstring | 1 | 0 | 0 | 100.0% | 100.0% |
| Mutable default argument | 1 | 0 | 0 | 100.0% | 100.0% |
| OS Command Injection | 3 | 0 | 0 | 100.0% | 100.0% |
| Overly long lines | 1 | 0 | 0 | 100.0% | 100.0% |
| Path Traversal | 2 | 0 | 0 | 100.0% | 100.0% |
| Permissive CORS | 1 | 0 | 0 | 100.0% | 100.0% |
| Possible Missing Authorization (IDOR) | 1 | 0 | 0 | 100.0% | 100.0% |
| SQL Injection | 3 | 0 | 2 | 100.0% | 60.0% |
| Sensitive Data in Logs | 1 | 0 | 0 | 100.0% | 100.0% |
| Server-Side Request Forgery | 2 | 0 | 0 | 100.0% | 100.0% |
| Swallowed exception | 1 | 0 | 0 | 100.0% | 100.0% |
| TLS Verification Disabled | 1 | 0 | 0 | 100.0% | 100.0% |
| Too Many Parameters | 1 | 0 | 0 | 100.0% | 100.0% |
| Trusting Client-Supplied Role | 1 | 0 | 0 | 100.0% | 100.0% |
| Unresolved TODO/FIXME | 1 | 0 | 0 | 100.0% | 100.0% |
| Unused import | 2 | 0 | 0 | 100.0% | 100.0% |
| Use of global state | 1 | 0 | 0 | 100.0% | 100.0% |
| Weak Cipher / ECB Mode | 1 | 0 | 0 | 100.0% | 100.0% |
| Weak Hash Algorithm | 2 | 0 | 0 | 100.0% | 100.0% |
| Wildcard import | 1 | 0 | 0 | 100.0% | 100.0% |
| XML External Entity (XXE) | 1 | 0 | 0 | 100.0% | 100.0% |

## Missed issues (false negatives)

- JavaVulnerable.java line 26: SQL Injection
- py_vulnerable_web.py line 37: SQL Injection

## False alarms (false positives)

- none
