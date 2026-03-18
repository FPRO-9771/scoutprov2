# Chunk 9: Admin Panel

## Goal
Build a simple admin panel for manual data management — override TBA data, manually create matches, manage games.

## Context
TBA is great but not always available or up to date. Match schedules drop right before competition. We need fallback manual entry. Keep it simple for v1 — enhance later.

## Tasks

### Admin Home
**Route:** `GET /admin`
**Template:** `templates/admin/index.html`

Dashboard with links to each management section:
- Games
- Events
- Teams
- Matches
- TBA Sync

### Game Management
**Route:** `GET /admin/games`, `POST /admin/games`
- List existing games
- Create new game (name, logo URL)
- Edit game score config (JSON editor — can be a simple textarea for v1)

### Event Management
**Route:** `GET /admin/events`, `POST /admin/events`
- List events
- Create event manually (name, location, date, game, TBA key)
- Edit existing events

### Team Management
**Route:** `GET /admin/teams`, `POST /admin/teams`
- List teams at current event
- Add team manually (number, name)
- Link/unlink teams to events

### Match Management
**Route:** `GET /admin/matches`, `POST /admin/matches`
- List matches for current event
- **Create match manually** — this is the critical one:
  - Match number
  - Red alliance: 3 team number inputs
  - Blue alliance: 3 team number inputs
- Edit existing match (change team assignments)
- Bulk create: paste a list of matches (nice to have, not required for v1)

### TBA Sync Controls
**Route:** `POST /admin/tba/sync-event`, `POST /admin/tba/sync-matches`
- Button: "Sync Event Teams from TBA" — re-import teams for current event
- Button: "Sync Matches from TBA" — re-import match schedule
- Show last sync timestamp
- Display sync results (teams added, matches added/updated)

### Admin Service (web/services/admin_service.py)
- Keep it thin — mostly CRUD wrappers
- `create_match(event_id, number, red_teams, blue_teams)`
- `update_match(match_id, red_teams, blue_teams)`
- Reuse import_service for TBA sync

## Files to Create
- `templates/admin/index.html`
- `templates/admin/games.html`
- `templates/admin/events.html`
- `templates/admin/teams.html`
- `templates/admin/matches.html`
- `templates/admin/tba_sync.html`
- `web/routes/admin.py` (implement all routes)
- `web/services/admin_service.py`

## Dependencies
Chunks 1-3 (models, TBA service, import service)

## Definition of Done
- Admin can create/edit games, events, teams, matches manually
- Admin can trigger TBA sync for teams and matches
- Match creation works (this is the most critical admin function)
- All forms work on mobile
- Simple, functional — no polish needed
