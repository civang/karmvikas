# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Project scaffolding: Flask app factory, layered `app/` structure (routes/services/repositories/models).
- Docker Compose stack: Flask backend, PostgreSQL, Redis.
- Health (`/health`) and readiness (`/ready`) endpoints.
- Base environment-driven configuration (`Development`/`Testing`/`Production`).
- Repository quality baseline: README, LICENSE (MIT), SECURITY.md, CONTRIBUTING.md, `.env.example`, `.gitignore`.
- SQLAlchemy models for all 11 domain entities with FKs, indexes, check/unique constraints, soft-delete and optimistic-concurrency mixins; initial Alembic migration.
- JWT authentication: access/refresh tokens, Redis-backed revocation (blacklist), refresh token rotation, RBAC via `role_required` decorator.
- `flask create-admin` CLI command to bootstrap the first admin account.
- Consistent JSON error envelope for validation, auth, and unexpected errors (no stack traces or internals ever exposed).
- Rate limiting on `/auth/login` and `/auth/forgot-password` (Redis-backed, shared across workers).
- Department and Designation CRUD APIs (admin/hr write, all authenticated read), with conflict handling for duplicate names and referential-integrity-protected deletes.
- Employee list/detail/update/soft-delete APIs with pagination, search, sort, and department/designation filters; `/employees/me` self-profile endpoint; field-level and record-level IDOR protection so employees can only edit their own limited fields.
- Attendance check-in/check-out APIs with same-day duplicate prevention and role-aware history filtering.
- Leave request lifecycle: apply, list, approve/reject (admin/hr only), automatic leave-balance seeding on employee creation, and balance-aware approval that blocks over-allocation.
- Frontend: responsive Bootstrap 5 UI (login, role-aware dashboard, employee directory with search/filter/pagination, self-service profile, attendance check-in/out, leave apply/approve/reject, department/designation admin) with dark mode, toasts, skeleton loaders, and empty states. Consumes the REST API exclusively via a shared JS client with automatic token refresh.
- UI polish: smooth transitions on theme toggle, sidebar nav, cards, buttons, and page content (previously instant/static).
- Announcements CRUD (admin/hr write, all authenticated read).
- Audit logging wired into login/logout, employee/department/designation deletes, leave approve/reject, and every authorization denial; admin-only `GET /audit-logs` API and page.
- Company Calendar: general event scheduling (holiday/meeting/deadline/event/other types), admin/hr manage, all authenticated view, filterable by type, date-range queryable API.
- Secure employee document management: server-generated (UUID) filenames, MIME/extension allowlist, files stored outside the public `static/` folder and served only via an authenticated, IDOR-protected download endpoint. Closes the file-upload-security gap from the original spec.
- Frontend pages for the Company Calendar and Audit Logs, plus a Documents section on the profile page (self) and employee modal (admin/hr).
- Visual redesign: custom design system (Inter typeface, indigo/violet palette, refined radii/shadows/typography for cards, tables, buttons, forms), redesigned sidebar (soft-highlight + accent-bar active state, gradient brand mark), gradient user avatar in the topbar, icon-led dashboard stat cards, and a split-screen login page with a branded panel. Consistent across light and dark mode.
- Real password reset via Brevo transactional email (signed, single-use, time-limited tokens), welcome emails on registration, dedicated Forgot/Reset Password pages.
- Automated test suite: 52 tests (pytest) against a real Postgres database covering auth (registration RBAC, login, refresh rotation/revocation, password reset single-use enforcement), employee self-service IDOR, attendance duplicate-prevention, leave balance business logic, and document upload/IDOR security. 85% overall coverage, 94-100% on the security-critical paths.
- GitHub Actions CI (`.github/workflows/tests.yml`): runs the full test suite with coverage plus `flake8` against Postgres/Redis service containers on every push/PR to `main`.
- OpenAPI 3.0 specification (`backend/app/static/openapi.yaml`) documenting all 40 endpoints with request/response schemas, auth requirements, and status codes; served as an interactive Swagger UI at `/api/docs`. Added 5 tests covering the docs route, spec validity/completeness, and the previously-untested `/health` and `/ready` ops endpoints.
- Mermaid architecture, request-lifecycle, and entity–relationship diagrams (`docs/architecture.md`), rendering natively on GitHub.

### Changed
- Replaced the legacy `Model.query.get(pk)` calls across all 7 repositories with the SQLAlchemy 2.0 `db.session.get(Model, pk)` API, removing `LegacyAPIWarning` deprecation warnings from the test run.
