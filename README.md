# EpiSim

AI-driven epidemic spread simulation platform for public health planning. This
is the initial foundation slice: authentication (Module 1) and disease
parameter configuration (Module 4), plus the project scaffold the rest of the
system's modules will build on.

Monorepo layout:

```
/backend   FastAPI (async) + SQLAlchemy/Alembic + Celery + fastapi-users
/frontend  Next.js (App Router, TypeScript) + Tailwind
```

## Prerequisites

- Docker + Docker Compose
- Node.js 20+ (only needed if you want to run `npm` commands outside the
  frontend container, e.g. `npm run generate-api`)

## Running locally

The backend and frontend are two independent Docker Compose stacks - **not**
one shared `docker-compose up` at the repo root. Run them in two terminals:

```bash
# Terminal 1
cd backend
cp .env.example .env
docker compose up

# Terminal 2
cd frontend
cp .env.example .env
docker compose up
```

The frontend container reaches the backend over `http://localhost:8000` (the
backend's host-mapped port), not a shared Docker network - the two compose
files are intentionally decoupled so each app can be stopped/rebuilt on its
own.

Once both are up:

- Frontend: http://localhost:3000
- Backend API + docs: http://localhost:8000/docs
- Mailhog (catches verification/reset emails in dev, nothing is really sent):
  http://localhost:8025
- MinIO console: http://localhost:9001

The backend's `docker-compose.yml` runs `alembic upgrade head` automatically
on startup, which creates the schema and seeds three built-in disease
presets (COVID-19, Cholera, Seasonal Influenza).

### First run

1. Open http://localhost:3000, click **Get Started**, and register an
   account (institution list comes from `GET /institutions`, empty until you
   add one directly in Postgres - institutions aren't seeded by default).
2. Open Mailhog (http://localhost:8025) to get the verification link.
3. Log in and you'll land on the dashboard shell, showing your name and role.
4. Visit **Disease Presets** to see the seeded built-ins and create your own.

## Backend

```bash
cd backend
cp .env.example .env
docker compose up
```

Services: `postgres` (PostGIS-enabled), `redis`, `minio`, `mailhog`,
`backend` (FastAPI + Uvicorn, reload on), `celery_worker`.

Note: since there's no Dockerfile (by design, for this initial scaffold -
see the setup notes), `backend` and `celery_worker` run `pip install -r
requirements.txt` as part of their startup command against a plain
`python:3.12-slim` image. The first `docker compose up` (or any
`--force-recreate`) takes several minutes to install `numpy`/`scipy`/`mesa`/
etc.; a plain `docker compose stop && docker compose up` (no recreate)
reuses the already-installed packages in that container's layer.

### Adding a new migration

Run this against a running `postgres` (e.g. with `docker compose up postgres
-d`, then from a host Python env with `requirements.txt` installed and
`DATABASE_URL` pointed at `localhost:<mapped-port>` instead of the in-network
`postgres` hostname):

```bash
alembic revision --autogenerate -m "add some_table"
alembic upgrade head
```

Commit the generated file under `alembic/versions/`.

### Tests

```bash
# with postgres/redis running (docker compose up postgres redis -d)
pip install -r requirements.txt
pytest
```

Tests run against the real database configured by `DATABASE_URL` (no mocks),
so they need a reachable Postgres.

## Frontend

```bash
cd frontend
cp .env.example .env
docker compose up
```

### Regenerating the API client types

Request/response types are generated from the backend's OpenAPI schema
rather than hand-written:

```bash
# with the backend running on localhost:8000
npm run generate-api
```

This writes `lib/api-types.ts`; `lib/api.ts` is a thin typed fetch wrapper
built on top of it.

## What's built so far

- **Module 1 - Auth**: registration, email verification (Mailhog in dev),
  login/logout, TOTP-based MFA setup/verify, password forgot/reset, session
  listing, institutions list, admin-only login-attempts audit log. Built on
  `fastapi-users` (JWT strategy) with custom route paths/behavior where the
  spec's endpoints didn't match its defaults (e.g. `/auth/login` logs every
  attempt to `login_attempts`, including ones with no matching account).
- **Module 4 - Disease Parameter Configuration**: CRUD for disease presets,
  seeded with 3 built-ins that reject edits.
- Frontend: landing page (rebuilt from the Magic Patterns prototype
  screenshots - palette and layout extracted from those, not invented),
  login, registration, a minimal dashboard shell, and the disease preset
  list/create/edit screens.

Not built yet (by design, per the initial scaffold scope): the other 12
modules (population data, simulation engine, SEIR/agent-based/network
models, interventions, geographic spread, healthcare capacity,
visualization, scenario comparison, reports, user management UI beyond
`/users/me`). `numpy`/`scipy`/`pandas`/`mesa` are already in
`requirements.txt` for when the simulation engine modules start, but nothing
uses them yet.

## Notes on a few implementation choices

- **MFA**: TOTP (RFC 6238) is hand-rolled on stdlib `hmac`/`hashlib` instead
  of adding `pyotp`, since the dependency list was fixed. See
  `app/core/security.py`.
- **MFA secret "encryption"**: a stdlib-only reversible cipher derived from
  `JWT_SECRET` - adequate for a local prototype; swap for real KMS-backed
  encryption before any real deployment.
- **Sessions vs. JWT**: the `sessions` table tracks issued tokens for
  listing/UX purposes, but the JWT strategy is stateless - `DELETE
  /users/me/sessions/{id}` (and `/auth/logout`) remove the tracked row, but
  the token itself remains cryptographically valid until it expires. A real
  deployment needing hard revocation would check a blacklist/allowlist on
  every request.
- **Trust bar logos**: the Magic Patterns prototype's landing page used real
  organizations' names/logos (UNICEF, WHO, a national ministry of health) as
  placeholder content. Since this is an unaffiliated academic prototype,
  the rebuilt landing page uses generic institution labels there instead of
  those specific names, to avoid implying an endorsement that doesn't exist.
  Everything else (layout, copy, color palette, section structure) is
  reproduced from the prototype as closely as possible.
