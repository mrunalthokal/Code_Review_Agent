# Python Secure Coding Guidelines

## Dangerous Functions
eval(), exec() and compile() on user input allow arbitrary code execution. pickle.loads and yaml.load on untrusted data allow code execution; use json or yaml.safe_load. Bandit flags these as B301 and B506.

## Safe Database Access
Use parameter placeholders: cursor.execute("SELECT * FROM users WHERE name = ?", (name,)). With SQLAlchemy use bound parameters or the ORM rather than string formatting.

## Subprocess and File Handling
Use subprocess.run with a list and shell=False. Validate file paths with pathlib and reject path traversal (../). Use tempfile.NamedTemporaryFile instead of predictable temp names.

## Cryptography and Randomness
Use the secrets module (not random) for tokens. Use hashlib.sha256 or better for integrity, never MD5 for security. Use the cryptography package for encryption. Always verify TLS certificates (never requests.get(verify=False)).

## Web Frameworks
Flask: disable debug mode in production, use Jinja2 autoescaping, add Flask-WTF CSRF protection. Django: keep CSRF middleware enabled, avoid mark_safe on user data, use the ORM.
