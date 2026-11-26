"""OWASP-mapped detection rules (data only). The engine lives in security_agent.py.
Each rule = regex patterns applied line by line, with an optional suppression regex."""
import re
from dataclasses import dataclass, field
from typing import Optional

from models import Severity as S

A01 = "A01:2021 Broken Access Control"
A02 = "A02:2021 Cryptographic Failures"
A03 = "A03:2021 Injection"
A05 = "A05:2021 Security Misconfiguration"
A07 = "A07:2021 Identification and Authentication Failures"
A08 = "A08:2021 Software and Data Integrity Failures"
A09 = "A09:2021 Security Logging and Monitoring Failures"
A10 = "A10:2021 Server-Side Request Forgery"

PY, JV = "python", "java"
SECRET_WORDS = r"(password|passwd|pwd|secret|api_?key|token|private_?key|access_?key|auth_?key)"


@dataclass
class Rule:
    id: str
    title: str
    owasp: str
    cwe: str
    severity: S
    langs: tuple
    patterns: list
    description: str
    recommendation: str
    unless: Optional[str] = None       # suppress if found within +-3 lines
    unless_file: Optional[str] = None  # suppress if found anywhere in the file
    compiled: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        self.compiled = [re.compile(p) for p in self.patterns]


RULES = [
    # ---- A03 Injection ----
    Rule("SEC-SQLI-PY", "SQL Injection", A03, "CWE-89", S.CRITICAL, (PY,), [
        r"\.execute\w*\(\s*f[\"']",
        r"\.execute\w*\(\s*[\"'].*[\"']\s*(\+|%)",
        r"\.execute\w*\(.*[\"']\s*\.format\(",
        r"\.execute\w*\(\s*\w+\s*\+",
        r"(?i)\b(query|sql|stmt)\w*\s*=\s*f[\"'].*\b(select|insert|update|delete)\b",
        r"(?i)\b(query|sql|stmt)\w*\s*=\s*[\"'].*\b(select|insert|update|delete)\b.*[\"']\s*(\+|%|\.format)",
    ], "SQL statement is built from strings; attacker input can change the query (e.g. ' OR '1'='1).",
       "Use parameterized queries: cursor.execute('... WHERE name = ?', (name,))."),
    Rule("SEC-SQLI-JV", "SQL Injection", A03, "CWE-89", S.CRITICAL, (JV,), [
        r"\.(executeQuery|executeUpdate|execute|prepareStatement|createQuery|createNativeQuery)\s*\(\s*\"[^\"]*\"\s*\+",
        r"\.(executeQuery|executeUpdate|execute|prepareStatement|createQuery|createNativeQuery)\s*\(\s*\w+\s*\+",
        r"(?i)\b(query|sql|stmt)\w*\s*=\s*\"[^\"]*\b(select|insert|update|delete)\b[^\"]*\"\s*\+",
    ], "SQL statement is built by string concatenation; attacker input can change the query.",
       "Use PreparedStatement with ? placeholders and setString()/setInt()."),
    Rule("SEC-CMDI-PY", "OS Command Injection", A03, "CWE-78", S.CRITICAL, (PY,), [
        r"\bos\.(system|popen)\s*\(", r"subprocess\.\w+\(.*shell\s*=\s*True"],
       "Shell commands can be hijacked with input such as '; rm -rf /'.",
       "Use subprocess.run([...], shell=False) with an argument list and validate input."),
    Rule("SEC-CMDI-JV", "OS Command Injection", A03, "CWE-78", S.CRITICAL, (JV,), [
        r"Runtime\.getRuntime\(\)\.exec\s*\([^)]*\+", r"new\s+ProcessBuilder\s*\([^)]*\+"],
       "Command string includes concatenated input.",
       "Pass arguments as a fixed list to ProcessBuilder and validate against an allow-list."),
    Rule("SEC-EVAL-PY", "Dangerous eval/exec", A03, "CWE-95", S.HIGH, (PY,), [r"(?<![\w.])(eval|exec)\s*\("],
       "eval()/exec() run arbitrary code if any input reaches them.",
       "Use ast.literal_eval or json.loads, or redesign without dynamic code execution."),
    Rule("SEC-XSS-PY", "Cross-Site Scripting (XSS)", A03, "CWE-79", S.HIGH, (PY,), [
        r"render_template_string\s*\(.*(\+|%|f[\"']|\.format)", r"\bMarkup\s*\(", r"\bmark_safe\s*\(", r"\|\s*safe\b"],
       "Unescaped user data can be rendered as HTML/JavaScript in the browser.",
       "Rely on auto-escaping, encode output by context, avoid Markup/mark_safe/|safe on user data, add CSP."),
    Rule("SEC-XSS-JV", "Cross-Site Scripting (XSS)", A03, "CWE-79", S.HIGH, (JV,), [
        r"getWriter\(\)\.(print|println|write)\s*\(.*(getParameter|\+)", r"\bout\.(print|println|write)\s*\(.*getParameter"],
       "Request data is written straight into the HTML response.",
       "Encode with OWASP Java Encoder (Encode.forHtml) or use a templating engine with escaping."),
    # ---- A02 Crypto / secrets ----
    Rule("SEC-SECRET", "Hardcoded Secret", A02, "CWE-798", S.HIGH, (PY, JV), [
        rf"(?i)\b\w*{SECRET_WORDS}\w*\s*=\s*[\"'][^\"'\s]{{4,}}[\"']",
        rf"(?i)[\"']\w*{SECRET_WORDS}\w*[\"']\s*:\s*[\"'][^\"'\s]{{4,}}[\"']"],
       "Credentials in source code leak through version control and builds.",
       "Load from environment variables or a secret manager, rotate the exposed secret, add .env to .gitignore."),
    Rule("SEC-SECRET-KEY", "Exposed Cloud Key / Private Key", A02, "CWE-798", S.CRITICAL, (PY, JV), [
        r"AKIA[0-9A-Z]{16}", r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"],
       "A real-looking cloud access key or private key is embedded in the code.",
       "Revoke and rotate immediately, then load from a secret manager."),
    Rule("SEC-HASH-PY", "Weak Hash Algorithm", A02, "CWE-327", S.MEDIUM, (PY,), [r"hashlib\.(md5|sha1)\s*\("],
       "MD5/SHA-1 are broken for security use.", "Use SHA-256+ for integrity; bcrypt/argon2 for passwords."),
    Rule("SEC-HASH-JV", "Weak Hash Algorithm", A02, "CWE-327", S.MEDIUM, (JV,),
       [r"MessageDigest\.getInstance\(\s*\"(MD5|SHA-?1)\""],
       "MD5/SHA-1 are broken for security use.", "Use SHA-256+ for integrity; BCrypt/Argon2 for passwords."),
    Rule("SEC-CRYPTO-JV", "Weak Cipher / ECB Mode", A02, "CWE-327", S.HIGH, (JV,),
       [r"Cipher\.getInstance\(\s*\"(DES|DESede|RC4|AES|[^\"]*/ECB/[^\"]*)\""],
       "DES/RC4/ECB (and plain \"AES\", which defaults to ECB) leak patterns and are insecure.",
       "Use AES/GCM/NoPadding with a random IV."),
    Rule("SEC-CRYPTO-PY", "Weak Cipher / ECB Mode", A02, "CWE-327", S.MEDIUM, (PY,),
       [r"MODE_ECB", r"\b(DES|ARC4)\.new\("], "Weak cipher or ECB mode in use.", "Use AES-GCM via the cryptography package."),
    Rule("SEC-TLS-PY", "TLS Verification Disabled", A02, "CWE-295", S.MEDIUM, (PY,),
       [r"verify\s*=\s*False", r"_create_unverified_context"],
       "Certificate checks are turned off, allowing man-in-the-middle attacks.", "Remove verify=False; trust a proper CA bundle."),
    Rule("SEC-RANDOM-PY", "Insecure Randomness", A02, "CWE-330", S.MEDIUM, (PY,),
       [r"(?i)(token|password|secret|session|otp|nonce|salt|key).*\brandom\.(random|randint|choice|randrange)\s*\("],
       "random is predictable and unsuitable for secrets.", "Use the secrets module (secrets.token_urlsafe)."),
    Rule("SEC-RANDOM-JV", "Insecure Randomness", A02, "CWE-330", S.LOW, (JV,), [r"new\s+(java\.util\.)?Random\s*\("],
       "java.util.Random is predictable; unsafe if used for tokens or keys.", "Use java.security.SecureRandom."),
    # ---- A08 Integrity ----
    Rule("SEC-DESER-PY", "Insecure Deserialization", A08, "CWE-502", S.HIGH, (PY,),
       [r"\b(c?[pP]ickle|marshal)\.loads?\s*\(", r"\byaml\.load\s*\((?!.*Safe)"],
       "Deserializing untrusted data can execute attacker code.", "Use json, or yaml.safe_load."),
    Rule("SEC-DESER-JV", "Insecure Deserialization", A08, "CWE-502", S.HIGH, (JV,), [r"new\s+ObjectInputStream\s*\("],
       "Java deserialization of untrusted streams can lead to remote code execution.",
       "Use JSON with explicit types or set an ObjectInputFilter."),
    # ---- A05 Misconfiguration ----
    Rule("SEC-DEBUG-PY", "Debug Mode Enabled", A05, "CWE-489", S.MEDIUM, (PY,),
       [r"\.run\(.*debug\s*=\s*True", r"^\s*DEBUG\s*=\s*True"],
       "Debug mode exposes stack traces and, in Flask, an interactive console.", "Disable debug in production via config."),
    Rule("SEC-BIND-PY", "Binds to All Interfaces", A05, "CWE-668", S.LOW, (PY,), [r"0\.0\.0\.0"],
       "Service listens on every network interface.", "Bind to 127.0.0.1 unless external access is required."),
    Rule("SEC-XXE-JV", "XML External Entity (XXE)", A05, "CWE-611", S.HIGH, (JV,),
       [r"(DocumentBuilderFactory|SAXParserFactory|XMLInputFactory)\.newInstance\(\)"],
       "XML parser created without disabling DTDs/external entities.",
       "Set disallow-doctype-decl to true (or FEATURE_SECURE_PROCESSING).",
       unless_file=r"disallow-doctype-decl|FEATURE_SECURE_PROCESSING|IS_SUPPORTING_EXTERNAL_ENTITIES"),
    Rule("SEC-CORS-JV", "Permissive CORS", A05, "CWE-942", S.MEDIUM, (JV,),
       [r"@CrossOrigin\(\s*(origins\s*=\s*)?\"\*\""], "Any website may call this endpoint.", "Restrict to trusted origins."),
    Rule("SEC-TMP-PY", "Insecure Temp File", A05, "CWE-377", S.MEDIUM, (PY,), [r"tempfile\.mktemp\("],
       "mktemp is vulnerable to race conditions.", "Use tempfile.NamedTemporaryFile or mkstemp."),
    # ---- CSRF ----
    Rule("SEC-CSRF-PY", "CSRF Protection Disabled", A01, "CWE-352", S.HIGH, (PY,),
       [r"@csrf_exempt", r"WTF_CSRF_ENABLED[\"'\]\s]*=\s*False"],
       "State-changing requests can be forged from other sites.", "Keep CSRF middleware enabled and send tokens."),
    Rule("SEC-CSRF-JV", "CSRF Protection Disabled", A01, "CWE-352", S.HIGH, (JV,), [r"csrf\(\)\.disable\(\)", r"csrf\([^)]*disable"],
       "State-changing requests can be forged from other sites.", "Keep Spring Security CSRF protection enabled."),
    # ---- A01 Access control ----
    Rule("SEC-IDOR-PY", "Possible Missing Authorization (IDOR)", A01, "CWE-639", S.MEDIUM, (PY,),
       [r"@\w+\.route\(.*<(int:|string:)?\w*id>"],
       "Route takes an object id but no authentication decorator is nearby.",
       "Require login and verify the current user owns/may access the object.",
       unless=r"login_required|jwt_required|auth|permission|require"),
    Rule("SEC-CLIENT-ROLE-PY", "Trusting Client-Supplied Role", A01, "CWE-639", S.HIGH, (PY,),
       [r"(?i)(is_admin|role|admin)\w*\s*=\s*request\.(args|form|json|cookies|values)"],
       "Privilege decisions are taken from user-controlled input.", "Derive roles from the server-side session/token."),
    Rule("SEC-ACCESS-JV", "Missing / Client-Controlled Access Check", A01, "CWE-285", S.MEDIUM, (JV,),
       [r"anyRequest\(\)\.permitAll\(\)", r"getParameter\(\s*\"(role|isAdmin|admin|user_?id)\"\s*\)"],
       "Endpoints are open to everyone or trust a client-supplied identity/role.",
       "Authenticate requests, apply @PreAuthorize, and use server-side identity."),
    Rule("SEC-PATH-PY", "Path Traversal", A01, "CWE-22", S.MEDIUM, (PY,), [r"open\s*\([^)]*request\.(args|form|files|values)"],
       "User-controlled path can read arbitrary files (../../etc/passwd).", "Normalise with pathlib and enforce a base directory."),
    Rule("SEC-PATH-JV", "Path Traversal", A01, "CWE-22", S.MEDIUM, (JV,),
       [r"new\s+(File|FileInputStream|FileReader)\s*\([^)]*getParameter"],
       "User-controlled path can read arbitrary files.", "Canonicalise the path and enforce a base directory."),
    # ---- A07 Auth ----
    Rule("SEC-AUTH-PY", "Insecure Authentication", A07, "CWE-798", S.HIGH, (PY,),
       [r"(?i)if\s+\w*password\w*\s*==\s*[\"']", r"jwt\.decode\(.*verify\s*=\s*False", r"(?i)algorithms\s*=\s*\[[\"']none[\"']"],
       "Password compared to a literal, or JWT signature not verified.",
       "Hash passwords (bcrypt/argon2), compare in constant time, always verify JWT signatures."),
    Rule("SEC-AUTH-JV", "Insecure Authentication", A07, "CWE-798", S.HIGH, (JV,),
       [r"(?i)password\w*\.equals\(\s*\"", r"(?i)\"[^\"]+\"\.equals\(\s*\w*password"],
       "Password compared with a literal string.", "Use BCryptPasswordEncoder.matches()."),
    # ---- A09 Logging ----
    Rule("SEC-LOG-JV", "Information Exposure via Stack Trace", A09, "CWE-209", S.LOW, (JV,), [r"\.printStackTrace\(\)"],
       "Stack traces can leak internals and bypass structured logging.", "Use a logger and show users a generic error."),
    Rule("SEC-LOG-SECRET", "Sensitive Data in Logs", A09, "CWE-532", S.LOW, (PY, JV),
       [r"(?i)\b(logging|logger|log|print|println)\b.*\(.*\b(password|passwd|secret|api_?key)\b\s*[,+)}]"],
       "Secrets written to logs are readable by anyone with log access.", "Never log credentials; mask sensitive values."),
    # ---- A10 SSRF ----
    Rule("SEC-SSRF-PY", "Server-Side Request Forgery", A10, "CWE-918", S.MEDIUM, (PY,),
       [r"requests\.(get|post|put|delete)\s*\(\s*(request\.\w+|f[\"'])"],
       "Server fetches a URL influenced by the user.", "Allow-list hosts and block internal IP ranges."),
    Rule("SEC-SSRF-JV", "Server-Side Request Forgery", A10, "CWE-918", S.MEDIUM, (JV,), [r"new\s+URL\s*\([^)]*getParameter"],
       "Server fetches a URL influenced by the user.", "Allow-list hosts and block internal IP ranges."),
]
