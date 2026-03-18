# Chunk 10: Polish & Deploy

## Goal
Production readiness — deploy to Heroku, error handling, final mobile UI pass, tests.

## Tasks

### Heroku Deployment
- Verify `Procfile`, `runtime.txt`, `requirements.txt` are correct
- Create Heroku app
- Set environment variables:
  - `DATABASE_URL` (Heroku Postgres addon)
  - `SECRET_KEY` (generate secure random)
  - `TBA_API_KEY` (from TBA account)
  - `FLASK_ENV=production`
- Run migrations on Heroku: `heroku run flask db upgrade`
- Run seed: `heroku run flask seed`
- Verify app boots and is accessible

### Error Pages
- `templates/errors/404.html` — "Page not found" with link back to home
- `templates/errors/500.html` — "Something went wrong" with link back to home
- Register error handlers in app factory

### Loading States
- Show spinner or "Loading..." on TBA data fetches (match prep screen)
- Disable save button after click to prevent double-submit
- Consider what happens with slow/no internet at venue

### Mobile UI Final Pass
- Test all screens on iPhone SE (smallest common phone)
- Test on iPad
- Verify touch targets are >= 48px
- Verify no horizontal scroll on any page
- Verify tabs, button grids, and modals work on mobile
- Verify navbar collapses properly

### Test Suite
- `tests/test_models.py` — model creation, relationships, constraints
- `tests/test_services.py` — service layer logic (robot, outcome, analytics)
- `tests/test_routes.py` — key route responses (login, home, scouting flows)
- `tests/conftest.py` — test app factory, test DB setup
- Run with: `pytest tests/ -v`

### Seed Data for Development
- `flask seed` should create a complete dev environment:
  - "Rebuilt" game
  - Team 9771 FPRO
  - Both events with teams
  - Some sample matches
  - A test user
- Optional: `flask seed-demo` with fake scouting data for testing analytics

### Final Checklist
- [ ] All routes work on mobile
- [ ] Save flows have confirmation modals
- [ ] Flash messages display correctly
- [ ] Session persistence works (cookie)
- [ ] TBA integration handles errors gracefully
- [ ] No console errors in browser
- [ ] Heroku deploy works
- [ ] Seed data populates correctly
- [ ] Tests pass

## Dependencies
All previous chunks (1-9)

## Definition of Done
- App is live on Heroku
- Team members can access it on their phones
- All scouting flows work end to end
- Error pages display for bad URLs
- Tests pass in CI
