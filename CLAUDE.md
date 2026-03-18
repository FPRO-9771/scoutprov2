# ScoutPro

Mobile-first FRC scouting app for team 9771 FPRO.

## Stack
- Flask + SQLAlchemy + Flask-Migrate
- Bootstrap 5 (mobile-first)
- Heroku (PostgreSQL in prod, SQLite in dev)
- The Blue Alliance API for event/match data

## Project Structure
- `app.py` — entry point, creates app via factory
- `config.py` — environment-based configuration
- `web/` — application package
  - `__init__.py` — `create_app()` factory
  - `extensions.py` — db and migrate instances
  - `models/` — one file per model
  - `routes/` — blueprints (one per concern)
  - `services/` — business logic (static methods)
  - `utils/` — shared helpers
- `templates/` — Jinja2 templates
- `static/` — CSS, JS, fonts
- `seed_data.py` — seeds team 9771

## Development
```bash
source .venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python seed_data.py
flask run --debug
```

## Database Migrations
```bash
flask db migrate -m "description"
flask db upgrade
```

## Testing
```bash
pytest
```

## Conventions
- Follow GPro patterns (PycharmProjects/generate-g-code)
- Short modules, separated concerns, DRY
- Service layer for business logic, thin routes
- JSON columns for flexible scouting data (game-specific)
- All v1 users auto-associated with team 9771
