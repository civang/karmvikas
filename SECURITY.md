# Security Policy

## Reporting a Vulnerability

This is a portfolio/educational project. If you find a security issue, please
open a private report via GitHub's "Report a vulnerability" feature rather than
a public issue.

## Security Practices in this Project

- Passwords are hashed with bcrypt; never stored or logged in plaintext.
- All secrets (DB credentials, JWT secret, Redis URL) are supplied via
  environment variables (`.env`, never committed — see `.env.example`).
- JWT access tokens are short-lived (15 min); refresh tokens are stored
  hashed in Redis and revoked on logout (blacklist).
- All list/detail endpoints enforce server-side authorization checks
  (role-based access control + ownership checks) to prevent IDOR and
  privilege escalation.
- Sensitive endpoints (login, password reset) are rate-limited.
- API error responses never expose stack traces, SQL, or internal paths.
- Docker containers run as a non-root user.

## Supported Versions

Actively maintained on the `main` branch only.
