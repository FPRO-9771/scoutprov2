# Chunk 3: The Blue Alliance Integration

## Goal
Connect to The Blue Alliance (TBA) API to pull event, team, and match data. Seed the DB with our two target events.

## Context
TBA API docs: https://www.thebluealliance.com/apidocs
Auth: `X-TBA-Auth-Key` header with API read key (stored in `TBA_API_KEY` env var).

For v1, we attend two events:
- Traverse City, MI
- Ferris State, MI

Team 9771 FPRO is seeded in Chunk 1. All TBA-imported teams get added to the Team table.

## Tasks

### TBA Service (web/services/tba_service.py)
Single module, all static methods. Keep each method small and focused.

**Methods:**
- `get_event(event_key)` — fetch event details
- `get_event_teams(event_key)` — list of teams at an event
- `get_event_matches(event_key)` — match schedule for an event
- `get_event_rankings(event_key)` — team rankings at an event
- `get_team_events(team_key, year)` — events a team has attended
- `get_team_event_status(team_key, event_key)` — team's rank/record at a specific event

**Internal helpers:**
- `_request(endpoint)` — shared GET with auth header, error handling, rate limit awareness
- `_parse_match(tba_match)` — extract match number, red/blue team lists from TBA match object

### Import Service (web/services/import_service.py)
Orchestrates pulling TBA data into our DB.

**Methods:**
- `import_event(tba_event_key, game_id)` — create/update Event row from TBA
- `import_event_teams(event_id)` — fetch teams for event from TBA, upsert into Team table, link via event_teams
- `import_event_matches(event_id)` — fetch matches from TBA, upsert into Match table

### Seed / CLI Commands
Flask CLI commands (registered in app factory):
- `flask seed` — create team 9771, create "Rebuilt" game, import the two target events + their teams
- `flask import-matches <event_key>` — pull match schedule (used right before competition when schedule drops)

### Error Handling
- TBA returns 304 Not Modified with `Last-Modified` headers — cache-friendly
- Handle network errors gracefully (log warning, don't crash)
- Handle missing data (some events may not have matches yet)

## Files to Create
- `web/services/tba_service.py`
- `web/services/import_service.py`
- CLI commands in `web/__init__.py` or `web/commands.py`

## Dependencies
Chunk 1 (models, DB)

## Definition of Done
- `flask seed` populates game, team 9771, both events, and teams at those events
- `flask import-matches <key>` pulls match schedule
- TBA service methods return clean Python dicts
- Works with no TBA key (graceful error message)
