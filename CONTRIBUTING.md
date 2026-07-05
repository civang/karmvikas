# Contributing

This is currently a solo portfolio project, but is structured to accept
contributions the way a professional open-source project would.

## Workflow

1. Branch from `develop`: `feature/<phase>-<short-description>`
2. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`
3. Open a PR into `develop` with a clear description and testing notes.
4. Ensure `flake8`, `black --check`, and `pytest` all pass before requesting review.

## Local Setup

See [README.md](README.md#getting-started).

## Running Tests

```bash
# One-time: create the test database and install dev dependencies
docker compose exec db psql -U hr_user -d hr_platform -c "CREATE DATABASE hr_platform_test;"
docker compose exec -u root backend pip install -r requirements-dev.txt

# Run the suite (from then on)
docker compose exec backend python -m pytest -v
docker compose exec backend python -m pytest --cov=app --cov-report=term-missing
```

Tests run against a real Postgres database (`hr_platform_test`), not mocks —
each test truncates all tables afterward for isolation. CI (`.github/workflows/tests.yml`)
runs the full suite plus `flake8` on every push/PR to `main`.
