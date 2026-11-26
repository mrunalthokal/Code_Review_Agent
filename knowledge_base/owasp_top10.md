# OWASP Top 10 Overview

The OWASP Top 10 is a standard awareness list of the most critical web application security risks. Use it as the baseline for severity classification of findings.

## A01 Broken Access Control
Users act outside their intended permissions. Examples: missing authorization checks, IDOR (changing an id in a URL to read another user's data), privilege escalation. Fix: deny by default, enforce checks server-side on every request, validate object ownership, log access failures.

## A02 Cryptographic Failures
Sensitive data exposed due to weak or missing cryptography. Examples: MD5/SHA1 for passwords, hardcoded keys, plain HTTP. Fix: use TLS, strong algorithms (AES-GCM, bcrypt/argon2), never store secrets in code.

## A03 Injection
Untrusted input is sent to an interpreter as part of a command or query. Includes SQL injection, OS command injection, LDAP injection and Cross-Site Scripting (XSS). Fix: parameterized queries, input validation with allow-lists, context-aware output encoding.

## A04 Insecure Design
Missing security controls at design level. Fix: threat modelling, secure design patterns, rate limiting, abuse-case testing.

## A05 Security Misconfiguration
Default credentials, verbose error messages, debug mode enabled in production, unnecessary services. Fix: hardened baseline configuration, disable debug, remove defaults.

## A06 Vulnerable and Outdated Components
Using libraries with known CVEs. Fix: maintain an inventory, run dependency scanners (OWASP Dependency-Check, Snyk), update regularly.

## A07 Identification and Authentication Failures
Weak passwords, no brute-force protection, session ids in URLs, missing MFA. Fix: strong password hashing, lockout/rate limiting, secure session management, MFA.

## A08 Software and Data Integrity Failures
Insecure deserialization, unsigned updates, untrusted CI/CD pipelines. Fix: verify signatures, avoid deserializing untrusted data (pickle, Java ObjectInputStream).

## A09 Security Logging and Monitoring Failures
Attacks go undetected without logs. Fix: log logins, access failures and validation failures; never log passwords or tokens; alert on anomalies.

## A10 Server-Side Request Forgery (SSRF)
The server fetches a user-supplied URL, letting attackers reach internal systems. Fix: allow-list destinations, block internal IP ranges, disable redirects.
