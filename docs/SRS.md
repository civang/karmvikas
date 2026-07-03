# Software Requirements Specification — Enterprise HR Management Platform

## 1. Scope

**In scope:** Auth (JWT/RBAC), Employee/Department/Designation CRUD, Attendance,
Leave requests, Payroll simulation, Performance reviews, Announcements, Employee
profile with photo upload, Dashboard analytics, Audit logging.

**Out of scope:** Real email delivery (mocked), real payment processing,
multi-tenancy, native mobile app.

## 2. Functional Requirements

See table in project history / regenerate on request — summarized: authentication,
RBAC enforcement, employee/department/designation CRUD, attendance recording,
leave lifecycle, payroll simulation, performance review cycles, announcements,
paginated/filterable/sortable search, audit trail, full OpenAPI documentation.

## 3. Non-Functional Requirements

Password hashing, env-based secrets, consistent error contract, layered
architecture (Route → Service → Repository → Model), normalized schema with
indexes, responsive frontend, rate limiting on sensitive endpoints, test
coverage ≥80% on services/repositories, CI on every push, Docker parity
between local and production.

## 4. Enterprise Enhancements (professionalism additions)

- Refresh token rotation + Redis-backed blacklist (real JWT logout/revocation)
- Soft delete + optimistic concurrency (`version_id`) on mutable records
- Async background job (Celery + Redis) for payroll generation
- API versioning under `/api/v1`
- `/health` and `/ready` operational endpoints
- Structured JSON logging

## 5. Architecture

```
Frontend (Bootstrap/JS) --HTTPS/JSON--> Flask REST API
    Routes (Blueprints) -> Services (business rules) -> Repositories (SQLAlchemy) -> Models
                                                              |
                                                         PostgreSQL
Redis: JWT blacklist + Celery broker
Celery worker: async payroll generation
```

## 6. Database Schema (summary)

`users` (auth identity) 1—1 `employees` (profile) N—1 `departments`,
`designations`. `employees` 1—N `attendance`, `leave_requests`, `leave_balances`,
`payroll`, `performance_reviews`. `announcements`, `audit_logs` reference
`users` as actor. Full ER diagram: `docs/er-diagram.png` (added in Phase 3).

## 7. API Design

All endpoints under `/api/v1`, resource-based (`/auth`, `/employees`,
`/departments`, `/designations`, `/attendance`, `/leaves`, `/payroll`,
`/reviews`, `/announcements`, `/dashboard`, `/audit-logs`), consistent
pagination/filter/sort/search query contract, uniform error envelope. Full spec:
`docs/api/openapi.yaml` (added progressively per phase).

## 8. Auth Flow

Login issues short-lived access JWT (15 min) + refresh token (7 days, hashed
in Redis). Refresh endpoint rotates tokens. Logout blacklists the refresh
token immediately. Every request re-validated server-side for role and
resource ownership (IDOR protection) — client-side checks are never trusted.

## 9. Testing Strategy

Unit tests (services, repositories mocked), integration tests (repositories
against real Postgres), API tests (full request/response cycle incl. RBAC
denial and negative/edge cases). Target ≥80% coverage on services/repositories.

## 10. Git & CI/CD

`main` (deployable) / `develop` (integration) / `feature/<phase>-<desc>`
branches, Conventional Commits, squash-merge PRs. GitHub Actions: lint + test
on PR, build (+deploy) on merge to `main`.

## 11. Deployment

Flask (gunicorn) + Celery worker on Render/Railway, managed PostgreSQL, managed
Redis (Upstash free tier), frontend served by Flask initially.

## 12. Roadmap

Phase 1 Planning (done) → 2 Setup (in progress) → 3 Database → 4 Auth →
5 Backend APIs → 6 Frontend → 7 Dashboard → 8 Testing → 9 Docker →
10 CI/CD → 11 Deployment → 12 Final Docs → 13 Interview Prep.
