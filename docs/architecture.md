# Architecture & Data Model

Diagrams below are written in [Mermaid](https://mermaid.js.org/) and render
natively on GitHub.

## System Architecture

The backend follows a strict layered architecture — each layer only calls the
layer directly beneath it.

```mermaid
flowchart TD
    Browser["Browser<br/>(Bootstrap 5 + vanilla JS)"]
    subgraph Flask["Flask REST API"]
        Routes["Routes / Blueprints<br/>app/api/*.py"]
        Services["Services<br/>business rules, authz, IDOR checks"]
        Repos["Repositories<br/>all SQLAlchemy queries"]
        Models["Models (SQLAlchemy ORM)"]
    end
    Postgres[("PostgreSQL<br/>system of record")]
    Redis[("Redis<br/>JWT revocation + rate limits")]
    Brevo["Brevo<br/>transactional email"]

    Browser -->|"HTTPS / JSON"| Routes
    Routes --> Services
    Services --> Repos
    Repos --> Models
    Models --- Postgres
    Services -.->|token blacklist / rate limit| Redis
    Services -.->|password reset / welcome mail| Brevo
```

## Request Lifecycle (example: approve a leave request)

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Route (leaves.py)
    participant J as JWT / RBAC
    participant S as LeaveService
    participant Repo as LeaveRepository
    participant DB as PostgreSQL

    C->>R: PATCH /api/v1/leaves/5/approve
    R->>J: verify token + role in (admin, hr)
    J-->>R: ok (else 401/403)
    R->>S: approve(leave_id=5, reviewer_id)
    S->>Repo: get_by_id(5)
    Repo->>DB: SELECT ...
    DB-->>Repo: LeaveRequest
    S->>S: check status == PENDING (else 409)
    S->>S: check remaining balance >= days (else 409)
    S->>DB: UPDATE leave + balance (commit)
    S-->>R: approved LeaveRequest
    R-->>C: 200 + JSON
```

## Entity–Relationship Diagram

```mermaid
erDiagram
    users ||--|| employees : "has profile"
    users ||--o{ leave_requests : "reviews"
    users ||--o{ announcements : "posts"
    users ||--o{ calendar_events : "creates"
    users ||--o{ employee_documents : "uploads"
    users ||--o{ audit_logs : "acts as"

    departments ||--o{ designations : "contains"
    departments ||--o{ employees : "employs"
    designations ||--o{ employees : "titles"

    employees ||--o{ attendance : "logs"
    employees ||--o{ leave_requests : "submits"
    employees ||--o{ leave_balances : "holds"
    employees ||--o{ employee_documents : "owns"

    users {
        int id PK
        string email UK
        string password_hash
        enum role
        bool is_active
    }
    employees {
        int id PK
        int user_id FK "UK, 1:1 with users"
        string first_name
        string last_name
        string phone
        date date_joined
        int department_id FK
        int designation_id FK
        bool is_deleted "soft delete"
        int version_id "optimistic lock"
    }
    departments {
        int id PK
        string name UK
        string description
    }
    designations {
        int id PK
        string title
        int department_id FK
    }
    attendance {
        int id PK
        int employee_id FK
        date date "unique(employee_id, date)"
        datetime check_in
        datetime check_out
        enum status
    }
    leave_requests {
        int id PK
        int employee_id FK
        enum leave_type
        date start_date
        date end_date
        enum status
        int reviewed_by FK
        string comment
    }
    leave_balances {
        int id PK
        int employee_id FK
        enum leave_type "unique(employee_id, leave_type)"
        int total
        int used
    }
    employee_documents {
        int id PK
        int employee_id FK
        enum document_type
        string stored_filename UK "server-generated UUID"
        string original_filename
        string content_type
        int file_size
        int uploaded_by FK
    }
    announcements {
        int id PK
        string title
        text body
        int posted_by FK
    }
    calendar_events {
        int id PK
        string title
        date date
        enum event_type
        string description
        int created_by FK
    }
    audit_logs {
        int id PK
        int user_id FK "nullable, append-only"
        string action
        string entity
        int entity_id
        string ip_address
        datetime timestamp
    }
```

## Key schema decisions

- **`users` and `employees` are separate tables** — authentication identity is
  kept independent of HR profile data (single responsibility at the schema level).
- **Soft delete** (`employees.is_deleted`) preserves referential integrity:
  attendance/leave/document rows keep pointing at a valid employee row.
- **Optimistic concurrency** (`employees.version_id`) — SQLAlchemy rejects a
  second concurrent update with a `StaleDataError` instead of silently
  overwriting the first user's change.
- **`audit_logs` is append-only** — no `updated_at`, no soft-delete column.
- **DB-level constraints as defense in depth**: `end_date >= start_date`,
  unique `(employee_id, date)` on attendance, unique `(employee_id, leave_type)`
  on balances — enforced by the database, not just the API layer.
