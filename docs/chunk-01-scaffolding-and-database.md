# Chunk 1: Project Scaffolding & Database

## Goal
Set up the project structure mirroring GPro patterns, define all database models, and verify the DB creates cleanly.

## Context
ScoutPro is a mobile-first scouting app for FRC team 9771 FPRO. We follow the same Flask + SQLAlchemy + Bootstrap 5 + Heroku stack as our GPro app (PycharmProjects/generate-g-code).

Code must be simple and maintainable by students on the team: short modules, separated concerns, very DRY.

## Tasks

### Project Structure
Create the directory tree:
```
scoutpro/
├── app.py                    # Entry point, app factory
├── config.py                 # Environment-based configuration
├── web/
│   ├── __init__.py           # create_app factory
│   ├── extensions.py         # SQLAlchemy + Migrate instances
│   ├── models/               # One file per model (keep them short)
│   │   ├── __init__.py       # Import all models for migration discovery
│   │   ├── game.py
│   │   ├── event.py
│   │   ├── team.py
│   │   ├── robot.py
│   │   ├── match.py
│   │   ├── outcome.py
│   │   └── user.py
│   ├── routes/               # Blueprints (one per concern)
│   ├── services/             # Business logic (one per domain)
│   └── utils/                # Shared helpers
├── static/
│   ├── css/
│   ├── js/
│   └── fonts/
├── templates/
├── migrations/               # Alembic (auto-generated)
├── tests/
├── docs/                     # Build plan documents
├── requirements.txt
├── Procfile
├── runtime.txt
└── CLAUDE.md
```

### Configuration (config.py)
Environment variables:
- `DATABASE_URL` — PostgreSQL (production) / SQLite (dev fallback)
- `SECRET_KEY` — session signing
- `TBA_API_KEY` — The Blue Alliance API read key
- `FLASK_ENV` — production or development

Handle Heroku's `postgres://` → `postgresql://` conversion (same as GPro).

### Database Models

**Game**
- `id` (Integer, PK)
- `name` (String, not null)
- `logo` (String, nullable) — path or URL to game logo
- `score_config` (JSONB) — array of score objects defining how the game is scored

**Event**
- `id` (Integer, PK)
- `game_id` (FK → Game)
- `name` (String, not null)
- `location` (String)
- `date` (Date)
- `tba_event_key` (String, unique) — e.g., "2026mitraverse"

**Team**
- `id` (Integer, PK)
- `number` (Integer, unique, not null)
- `name` (String)
- `tba_key` (String, unique) — e.g., "frc9771"

**event_teams** (association table)
- `event_id` (FK → Event)
- `team_id` (FK → Team)

**Robot**
- `id` (Integer, PK)
- `team_id` (FK → Team)
- `game_id` (FK → Game)
- `scouting_data` (JSONB) — for Rebuilt 2025-2026:
  ```json
  {
    "drive_system": "tank" | "swerve",
    "ground_intake": true | false,
    "shooter_system": "fixed" | "turret",
    "climb": "none" | "L1" | "L2" | "L3"
  }
  ```
- Unique constraint on (team_id, game_id) — one robot per team per game

**Match**
- `id` (Integer, PK)
- `event_id` (FK → Event)
- `number` (Integer, not null)
- `red_teams` (JSONB) — array of team numbers [9771, 1234, 5678]
- `blue_teams` (JSONB) — array of team numbers [4321, 8765, 2468]
- `tba_match_key` (String, nullable) — e.g., "2026mitraverse_qm1"
- Unique constraint on (event_id, number)

**Outcome**
- `id` (Integer, PK)
- `match_id` (FK → Match)
- `team_id` (FK → Team)
- `user_id` (FK → User)
- `scouting_data` (JSONB) — for Rebuilt 2025-2026:
  ```json
  {
    "auton_balls": 0-5,
    "auton_climb": 0-3,
    "teleop_balls": 0-5,
    "teleop_climb": 0-3,
    "teleop_defense": 0-3
  }
  ```
- `created_at` (DateTime, UTC)
- Unique constraint on (match_id, team_id, user_id)

**User**
- `id` (Integer, PK)
- `team_id` (FK → Team)
- `username` (String, not null)
- Unique constraint on (team_id, username)

### Deployment Files
- `requirements.txt` — Flask, SQLAlchemy, Migrate, Gunicorn, psycopg2-binary, requests
- `Procfile` — `web: gunicorn app:app`
- `runtime.txt` — `python-3.13.0`

### CLAUDE.md
Document project conventions, how to run locally, key patterns.

### Seed Data
- Team 9771 "FPRO" must be seeded on first run (or via a CLI command)
- All users created in v1 are auto-associated with team 9771

### Verification
- `flask db init` / `flask db migrate` / `flask db upgrade` all pass
- App starts with `flask run`
- All tables created in SQLite dev DB
- Team 9771 exists in DB after seed

## Dependencies
None — this is the first chunk.

## Definition of Done
- All files created, app boots, DB migrates cleanly, tests pass for model creation.
