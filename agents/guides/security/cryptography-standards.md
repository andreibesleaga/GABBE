# Guide: Cryptography & Secrets Management (2026)
<!-- Encryption, Hashing, Key Management, TLS -->

---

## 1. Data in Transit
All network communication must be encrypted.

- **Standard**: TLS 1.3 is mandatory for all external traffic. TLS 1.2 is the absolute minimum acceptable fallback.
- **Internal Traffic**: Use mTLS (Mutual TLS) within service meshes (e.g., Istio, Linkerd) so internal services authenticate each other.
- **HSTS**: Always return `Strict-Transport-Security` headers to force browsers to use HTTPS.

## 2. Data at Rest (Encryption)
Encrypt sensitive data before storing it in databases or file systems.

- **Symmetric Encryption**: Use **AES-256-GCM** or **ChaCha20-Poly1305**. Both provide authenticated encryption (detects tampering).
- **Asymmetric Encryption**: For new RSA keys use **RSA-3072** or higher (RSA-2048 is the absolute minimum for legacy interop). For Elliptic Curve Cryptography, keep signatures and key exchange separate: use **Ed25519** for *digital signatures* and **X25519** for *key exchange / key agreement* — Ed25519 is a signature scheme only and must not be used for key exchange.
- **Database level**: Utilize provider-level Transparent Data Encryption (TDE) for full disk encryption, plus application-level encryption for highly sensitive column data (e.g., SSNs, medical data).

## 3. Hashing (Passwords & Integrity)
Hashing is one-way. You cannot decrypt a hash.

- **Passwords**: Use **Argon2id**. If Argon2 is unavailable, use **Bcrypt** (work factor 12+). NEVER use MD5 or SHA-1 for passwords.
- **Salts**: A unique, random salt must be generated for every password.
- **Data Integrity**: Use **SHA-256** or **SHA-3** to verify file/message integrity.

## 4. Secrets Management
API keys, database credentials, and certificates are secrets.

- **NEVER hardcode secrets in source code**.
- **NEVER commit `.env` files** containing real secrets to version control. Use `.env.example` as a template.
- **Storage**: Use dedicated secret managers (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, Google Secret Manager).
- **Access**: Applications should retrieve secrets dynamically at startup or runtime via IAM roles/identities, not hardcoded bootstrap tokens.
- **Rotation**: Design systems to support zero-downtime automated secret rotation.

## 5. Random Number Generation
- **CSPRNG**: Always use Cryptographically Secure Pseudo-Random Number Generators (e.g., `/dev/urandom`, `crypto.randomBytes()`, `secrets` module in Python) for tokens, keys, and session IDs.
- Never use standard `Math.random()` or `rand()` for security purposes.

## 6. Post-Quantum Readiness & Crypto-Agility
A sufficiently large quantum computer would break RSA and classical ECC ("harvest now, decrypt later" makes long-lived secrets a present-day concern).

- **Standardized PQC**: NIST has standardized **ML-KEM (FIPS 203, formerly CRYSTALS-Kyber)** for key encapsulation and **ML-DSA (FIPS 204, formerly CRYSTALS-Dilithium)** for signatures. Prefer **hybrid** schemes (classical + PQC) during the transition so security holds even if one primitive is broken.
- **Crypto-agility**: Design systems so algorithms, key sizes, and providers can be swapped without re-architecting. Reference algorithms by configurable identifier rather than hardcoding them, and version your ciphertext/key material so a future rotation to PQC is a configuration change, not a rewrite.
