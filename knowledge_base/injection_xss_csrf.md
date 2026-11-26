# Injection, XSS and CSRF Prevention

## SQL Injection
Occurs when user input is concatenated into a SQL string, e.g. "SELECT * FROM users WHERE name = '" + name + "'". An attacker can input ' OR '1'='1 to read all rows. Severity: Critical. Remediation: always use parameterized queries or prepared statements. Never build SQL with string concatenation or f-strings. Apply least-privilege database accounts.

## Cross-Site Scripting (XSS)
Attacker-controlled input is rendered in a page as executable script. Types: reflected, stored, DOM-based. Severity: High. Remediation: encode output for its context (HTML, attribute, JS, URL), use template engines with auto-escaping, set a Content-Security-Policy header, avoid innerHTML and eval.

## Cross-Site Request Forgery (CSRF)
A malicious site makes the victim's browser send authenticated requests to your application. Severity: Medium to High. Remediation: anti-CSRF tokens on state-changing requests, SameSite=Lax or Strict cookies, verify Origin/Referer headers, require re-authentication for sensitive actions.

## OS Command Injection
Input passed to a shell, e.g. os.system("ping " + host) in Python or Runtime.exec in Java. Severity: Critical. Remediation: avoid shell calls, use argument lists (subprocess.run([...], shell=False)), validate input against an allow-list.
