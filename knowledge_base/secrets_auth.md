# Hardcoded Secrets and Authentication

## Hardcoded Secrets
API keys, passwords, tokens or private keys written in source code leak through version control. Severity: High to Critical. Remediation: load secrets from environment variables or a secret manager (Vault, AWS Secrets Manager), add .env to .gitignore, rotate any exposed credential immediately, run secret scanners (gitleaks, Bandit B105/B106).

## Password Storage
Never store plaintext or fast hashes (MD5, SHA1, SHA256 alone). Use bcrypt, scrypt or Argon2 with per-user salt. In Python use passlib or bcrypt; in Java use BCryptPasswordEncoder from Spring Security.

## Session and Token Management
Generate session ids with a cryptographically secure random generator, set Secure, HttpOnly and SameSite cookie flags, expire sessions, regenerate the id after login. Validate JWT signature, expiry and algorithm; reject alg=none.

## Access Control Best Practices
Enforce authorization on the server for every endpoint, apply least privilege and role-based access control, check resource ownership to prevent IDOR, and deny by default.
