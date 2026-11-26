# Java Secure Coding Guidelines

## SQL Access
Use PreparedStatement with ? placeholders instead of Statement with concatenated strings. Example: PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name = ?"); ps.setString(1, name). With JPA use named parameters.

## Deserialization
Never deserialize untrusted data with ObjectInputStream. Use JSON with explicit types, or apply a deserialization filter (ObjectInputFilter).

## XML Processing (XXE)
Disable external entities: factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true). Applies to DocumentBuilderFactory, SAXParserFactory and XMLInputFactory.

## Cryptography
Use AES/GCM instead of DES or ECB mode. Use SecureRandom, not java.util.Random, for tokens. Hash passwords with BCrypt or Argon2. Avoid MD5 and SHA-1. SpotBugs and FindSecBugs detect many of these issues.

## Input Validation and Error Handling
Validate input with allow-lists using Bean Validation annotations. Do not expose stack traces to users. Never catch and ignore exceptions silently. Close resources with try-with-resources to avoid leaks.

## Spring Security
Enable CSRF protection, use method-level security (@PreAuthorize) for access control, and store secrets outside application.properties in version control.
