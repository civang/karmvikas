# Karmvikas HR — Enterprise HR Management Platform

An API-first Human Resource Management System covering the full employee
lifecycle — authentication & RBAC, employee/department/designation
management, attendance, leave, a company-wide event calendar, secure
document storage, org announcements, and a full audit trail — built with
production-grade backend engineering practices and a hand-built, responsive
frontend that consumes the REST API exclusively.

This project is built as a portfolio piece demonstrating professional
software engineering: layered architecture, defense-in-depth security,
verified (not assumed) correctness, and honest documentation of what is and
isn't done yet.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Security](#security)
- [Database Schema](#database-schema)
- [API Overview](#api-overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Roles & Permissions](#roles--permissions)
- [Project Status](#project-status)
- [License](#license)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask (REST API), Flask-SQLAlchemy, Flask-Migrate (Alembic) |
| Database | PostgreSQL 16 |
| Cache / Token store | Redis 7 (JWT revocation, rate-limit storage) |
| Auth | Flask-JWT-Extended (access + refresh tokens), Flask-Bcrypt |
| Validation / Serialization | Marshmallow |
| Rate limiting | Flask-Limiter (Redis-backed) |
| Frontend | HTML5, Bootstrap 5.3, vanilla JavaScript (no framework, no build step) |
| Fonts / Icons | Google Fonts (Inter), Bootstrap Icons |
| DevOps | Docker, Docker Compose |
| Migrations | Alembic (via Flask-Migrate) |
| Testing | pytest, run against a real Postgres database (not mocks) |
| CI | GitHub Actions |
| Email | Brevo (transactional email API) |

No frontend framework or bundler is used deliberately — the UI is served
directly by Flask (Jinja templates for layout shell + vanilla JS calling the
JSON API), keeping the "one repo, API-first" architecture simple to reason
about end-to-end.

---

## Architecture

The backend follows a strict layered architecture. Each layer only calls the
layer directly below it:

```
Browser (Bootstrap + vanilla JS)
        │  fetch() → JSON over HTTPS
        ▼
┌────────────────────────────────────────────┐
│                Flask REST API                │
│  ┌────────────────────────────────────────┐  │
│  │ Routes (Blueprints)                     │  │  HTTP concerns only:
│  │   app/api/*.py, app/web.py               │  │  parse request → call
│  ├────────────────────────────────────────┤  │  service → return
│  │ Services (business logic)               │  │  response
│  │   app/services/*.py                       │  │
│  ├────────────────────────────────────────┤  │  Authorization rules,
│  │ Repositories (data access)               │  │  IDOR checks, business
│  │   app/repositories/*.py                   │  │  invariants live here
│  ├────────────────────────────────────────┤  │
│  │ Models (SQLAlchemy ORM)                 │  │  All SQL lives here —
│  │   app/models/*.py                         │  │  nowhere else in the
│  └────────────────────────────────────────┘  │  codebase
└────────────────────────────────────────────┘
        │                              │
        ▼                              ▼
┌───────────────┐              ┌───────────────┐
│  PostgreSQL    │              │     Redis      │
│  (system of    │              │  JWT revocation │
│   record)      │              │  rate-limit store│
└───────────────┘              └───────────────┘
```

**Why this layering:** Routes never touch the database directly, so they
stay thin and testable. Services hold business rules (e.g. "an employee
can't approve their own leave," "leave balance can't go negative") —
authorization and business logic live here, not scattered across routes.
Repositories isolate all SQLAlchemy usage, so the ORM could be swapped or
cached without touching business logic. This is the Repository + Service
pattern applied consistently across all 10 resource domains in the app.

---

## Features

### Authentication & Access Control
- JWT access (15 min) + refresh (7 days) tokens
- Refresh token rotation with Redis-backed revocation (real-time logout, not just expiry)
- Role-based access control (Admin / HR / Employee) enforced server-side on every route
- Password hashing via bcrypt, strength-validated on registration
- Rate-limited login and forgot-password endpoints (Redis-backed, safe across multiple workers)
- `flask create-admin` CLI command to bootstrap the first admin account

### Employee Management
- Full employee directory: paginated, searchable, sortable, filterable by department/designation
- Self-service profile editing (field-level restricted — employees can only edit their own name/phone, not department/designation)
- Soft delete with optimistic-concurrency versioning (`version_id`) to prevent silent overwrite conflicts
- Department & Designation CRUD (admin/HR), with referential-integrity-protected deletes

### Attendance
- Check-in / check-out with same-day duplicate prevention
- Role-aware history: employees see only their own records, admin/HR can view anyone's

### Leave Management
- Apply / list / approve / reject workflow
- Automatic leave-balance seeding on employee creation (casual/sick/earned/unpaid)
- Balance-aware approval — blocks approval if it would exceed the employee's remaining balance
- Employees cannot approve their own leave requests, even by guessing the endpoint

### Company Calendar
- General event scheduling: holidays, meetings, deadlines, and other company events
- Filterable by event type, date-range queryable
- Admin/HR manage, all authenticated users view

### Secure Employee Documents
- Upload employee documents (ID proof, offer letter, resume, certificates)
- Server-generated (UUID) filenames — the client-supplied filename is **never** used for storage
- MIME type and extension allowlist (PDF/PNG/JPG only), 5MB size cap
- Files stored **outside** the public `static/` folder and served only via an authenticated,
  IDOR-protected download endpoint — a direct static URL cannot reach them
- IDOR protection: an employee can only view/download/delete their own documents; admin/HR can access any

### Announcements
- Org-wide announcements (admin/HR post, all authenticated users read)

### Audit Logging
- Every login, logout, delete, leave approval/rejection, calendar event change, and
  **authorization denial** is logged with actor, action, entity, timestamp, and IP address
- Admin-only audit log viewer

### Frontend
- Fully responsive (mobile / tablet / desktop) Bootstrap 5 UI
- Dark mode with no flash-of-wrong-theme (theme applied before first paint, not after JS load)
- Role-aware navigation and dashboard (different views for Admin/HR vs Employee)
- Custom design system: Inter typeface, indigo/violet palette, refined shadows/radii,
  split-screen branded login page, gradient avatar/brand mark
- Toasts, skeleton loaders, empty states, smooth transitions throughout

---

## Security

Security was designed in at every layer, not bolted on:

| Concern | Mitigation |
|---|---|
| SQL injection | SQLAlchemy ORM exclusively; no raw string-built SQL anywhere |
| Password storage | bcrypt hashing; passwords never logged, never returned in any API response |
| JWT revocation | Redis-backed blacklist checked on every request; refresh rotation invalidates old tokens immediately |
| IDOR (Insecure Direct Object Reference) | Every "own resource" endpoint re-derives the caller's identity server-side from the JWT, never trusts an ID in the URL for non-privileged roles |
| Privilege escalation | Role embedded as a signed JWT claim; `role_required()` decorator checked before any route body executes |
| Brute force | Rate limiting on `/auth/login` and `/auth/forgot-password`, Redis-backed so it's enforced across all gunicorn workers |
| User enumeration | `/auth/forgot-password` returns an identical response whether or not the email exists |
| File upload attacks | Extension + MIME allowlist, server-generated filenames, files stored outside the public static path, size-capped |
| Information disclosure | Global error handler never leaks stack traces, SQL, or internal paths — consistent JSON error envelope for every failure mode |
| Secrets management | All secrets loaded from environment variables (`.env`, gitignored); `.env.example` ships with empty values only; app fails to start (not silently defaults) if a required secret is missing |
| Audit trail | Every sensitive action and every authorization denial is logged with actor/IP/timestamp |
| Data integrity | Optimistic concurrency control (`version_id`) prevents silent lost-update conflicts on concurrent edits |
| Docker | Non-root container user, slim base image, no secrets baked into the image |

---

## Database Schema

11 tables, fully normalized, with foreign keys and indexes on all lookup columns:

```
users ──1:1── employees ──N:1── departments
                  │        │
                  │        └──N:1── designations
                  │
                  ├──1:N── attendance
                  ├──1:N── leave_requests ──N:1── users (reviewed_by)
                  ├──1:N── leave_balances
                  └──1:N── employee_documents ──N:1── users (uploaded_by)

announcements ──N:1── users (posted_by)
calendar_events ──N:1── users (created_by)
audit_logs ──N:1── users (nullable, actor)
```

Notable schema decisions:
- `users` (auth identity) and `employees` (HR profile) are separate tables —
  keeps authentication concerns independent of HR data.
- Money/salary-style fields, where they existed, always used `Numeric`, never
  `Float` (avoids floating-point rounding errors).
- `end_date >= start_date` and `rating` ranges are enforced as **database**
  check constraints, not just API validation — defense in depth.
- `audit_logs` is deliberately append-only (no `updated_at`, no soft-delete).

---

## API Overview

All endpoints are versioned under `/api/v1`. Full list of resource groups:

| Resource | Base path | Notes |
|---|---|---|
| Auth | `/api/v1/auth` | register (admin/HR only), login, refresh, logout, forgot-password |
| Departments | `/api/v1/departments` | CRUD |
| Designations | `/api/v1/designations` | CRUD |
| Employees | `/api/v1/employees` | list (paginated/search/filter/sort), detail, update, soft-delete, `/me` |
| Attendance | `/api/v1/attendance` | check-in, check-out, history |
| Leave | `/api/v1/leaves` | apply, list, approve, reject, balances |
| Calendar | `/api/v1/calendar-events` | list, create, delete |
| Documents | `/api/v1/employees/{id}/documents`, `/api/v1/documents/{id}/download` | upload, list, download, delete |
| Announcements | `/api/v1/announcements` | list, create, delete |
| Audit Logs | `/api/v1/audit-logs` | admin-only list |
| Ops | `/health`, `/ready` | liveness/readiness probes |

Every list endpoint that returns a collection supports a consistent query
contract: `?page=&per_page=&sort=&search=&filter[field]=`. Every error
response follows the same envelope:

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": {...} } }
```

---

## Project Structure

```
karmvikas/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # application factory (create_app)
│   │   ├── config.py            # env-driven Dev/Test/Prod config
│   │   ├── extensions.py        # db, jwt, bcrypt, cors, limiter singletons
│   │   ├── models/               # SQLAlchemy models (one file per entity)
│   │   ├── repositories/         # data access layer
│   │   ├── services/             # business logic layer
│   │   ├── schemas/              # Marshmallow request/response schemas
│   │   ├── api/                  # Flask Blueprints (one per resource)
│   │   ├── errors/                # custom exceptions + global error handlers
│   │   ├── utils/                # decorators, pagination, audit logging, Redis client
│   │   ├── web.py                 # server-rendered page routes (frontend shell)
│   │   ├── templates/             # Jinja layout + page templates
│   │   └── static/                # css/, js/ (vanilla JS API client + pages)
│   ├── migrations/                # Alembic migration history
│   ├── tests/                      # pytest suite (auth, IDOR, business logic, security)
│   ├── requirements.txt / requirements-dev.txt
│   └── Dockerfile
├── docker-compose.yml              # backend + PostgreSQL + Redis
├── .github/workflows/tests.yml     # CI: pytest + flake8 on every push/PR
├── .env.example
├── docs/
│   └── SRS.md                      # full software requirements spec
├── CHANGELOG.md
├── SECURITY.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Getting Started

**Prerequisites:** Docker Desktop.

```bash
# 1. Copy environment template and fill in real secrets (never commit .env)
cp .env.example .env

# 2. Bring up the stack (Flask + PostgreSQL + Redis)
docker compose up --build

# 3. Bootstrap the first admin account
docker compose exec backend flask create-admin

# 4. Open the app
# UI:      http://localhost:5000/login
# Health:  http://localhost:5000/health
```

Database migrations run via Alembic:

```bash
docker compose exec backend flask db upgrade      # apply migrations
docker compose exec backend flask db migrate -m "message"   # generate a new one after model changes
```

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Required variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session/signing secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string (JWT revocation + rate limiting) |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Postgres container credentials |
| `CORS_ORIGINS` | Allowed CORS origin(s) for the API |

The app deliberately **fails to start** if a required secret is missing,
rather than silently falling back to an insecure default.

---

## Roles & Permissions

| Capability | Employee | HR | Admin |
|---|:---:|:---:|:---:|
| View own profile / attendance / leave / documents | ✅ | ✅ | ✅ |
| Edit own name/phone | ✅ | ✅ | ✅ |
| View employee directory | ✅ | ✅ | ✅ |
| Create/edit employees, departments, designations | ❌ | ✅ | ✅ |
| Approve/reject leave | ❌ | ✅ | ✅ |
| Post announcements / manage calendar | ❌ | ✅ | ✅ |
| View any employee's documents | ❌ | ✅ | ✅ |
| View audit logs | ❌ | ❌ | ✅ |

All of the above is enforced **server-side** on every request — the frontend
hiding a button is a UX convenience, never the actual security boundary.

---

## Project Status

Actively developed, not yet production-deployed. Honest status as of now:

**Done:** planning/SRS, project scaffolding, database schema + migrations,
authentication & RBAC, all backend resource APIs, full responsive frontend,
custom design system, security hardening pass, real password reset via email,
automated test suite (52 tests, 85% coverage, run against real Postgres),
CI pipeline (GitHub Actions), Git history.

**Not yet done:**
- Production deployment (Render/Neon/Upstash accounts not yet created).
- OpenAPI/Swagger spec file, ER diagram image, architecture diagram image.

See [CHANGELOG.md](CHANGELOG.md) for the detailed, dated history of what's
been built, and [`docs/SRS.md`](docs/SRS.md) for the original requirements
and design rationale.

---

## License

[MIT](LICENSE)
