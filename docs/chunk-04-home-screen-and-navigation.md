# Chunk 4: Home Screen & Navigation

## Goal
Build the main hub screen users see after login + event selection, with the 4 primary actions and team search.

## Context
After selecting a user and event, this is the home screen. It needs to be dead simple — big buttons, mobile-first. Users are students at a competition, often standing, holding a phone.

## Tasks

### Home Screen (templates/home.html)
**Route:** `GET /home`

Layout (top to bottom):
1. Event name displayed prominently at top
2. **Search box** — type a team number, hit enter/go, navigate to that team's page
3. **4 big action buttons** in a 2x2 grid (mobile) or row (tablet):
   - Match Prep (icon: clipboard/strategy)
   - Scout a Match (icon: eye/target)
   - Scout a Robot (icon: robot/wrench)
   - (future: Analytics — can be placeholder or hidden for now)

Buttons should be large, colorful, easy to tap. Use the brand color palette.

### Blueprints & Routes
Set up all route blueprints now (even if pages are stubs):

- **main_bp** (no prefix): `/login`, `/logout`, `/events`, `/home`
- **scouting_bp** (`/scout`): `/scout/match/...`, `/scout/robot/...`
- **teams_bp** (`/teams`): `/teams/<number>`, `/teams/search`
- **matches_bp** (`/matches`): `/matches/prep`, `/matches/<id>`
- **admin_bp** (`/admin`): admin panel routes

### Team Search
- `GET /teams/search?q=<number>` — redirects to `/teams/<number>`
- If team not found at this event, show a friendly message

### Session Guards
- Middleware or decorator: if no user in session, redirect to `/login`
- If no event in session, redirect to `/events`
- Home and all scouting routes require both

## Files to Create/Modify
- `templates/home.html`
- `web/routes/main.py` (add home route)
- `web/routes/scouting.py` (stub)
- `web/routes/teams.py` (search + team page stub)
- `web/routes/matches.py` (stub)
- `web/routes/admin.py` (stub)
- `web/auth.py` — session guard decorator

## Dependencies
Chunks 1-2 (DB, base UI, login flow)

## Definition of Done
- After login + event select, user sees home screen with 4 buttons
- Search box finds teams at the event
- All blueprints registered, stub routes return placeholder pages
- Session guards redirect properly
