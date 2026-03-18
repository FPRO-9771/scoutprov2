# Chunk 7: Match Prep (UI Flow 3.B)

## Goal
Build the match prep screen — our team's strategy view showing who we're playing with/against and what we know about them.

## Context
This is the strategy screen. Before a match, team members pull this up to see:
- Who are our alliance partners?
- Who are we playing against?
- How good are they? (TBA data + our scouting data)

Only shows matches where team 9771 is participating.

## Tasks

### Match Prep List
**Route:** `GET /matches/prep`
**Template:** `templates/matches/prep_list.html`

- List of matches where team 9771 is in either red or blue alliance
- Show match number, which alliance we're on (red/blue badge)
- Ordered by match number
- Tap a match → go to match prep detail

### Match Prep Detail
**Route:** `GET /matches/prep/<match_id>`
**Template:** `templates/matches/prep_detail.html`

Layout — grouped by alliance:

**Red Alliance** (red-tinted section)
- Team cards for each of the 3 red teams

**Blue Alliance** (blue-tinted section)
- Team cards for each of the 3 blue teams

**Each team card shows:**
1. Team number + name (prominent)
2. **Past Event Performance** (from TBA):
   - Previous events attended this season
   - Final rank at each event
   - Displayed as: "Event Name — Rank #X"
3. **Current Event Rank** (from TBA):
   - Current ranking at this event (if available)
4. **Our Scouting Data** (from Outcome table):
   - Avg Auton Balls | Avg Auton Climb
   - Avg Teleop Balls | Avg Teleop Defense | Avg Teleop Climb
   - Number of matches scouted
   - Display as compact stat row
5. **Robot Build** (from Robot table, if scouted):
   - Drive / Intake / Shooter / Climb as small badges

Highlight team 9771's card differently (it's us!).

### TBA Data Fetching
For the match prep screen, we need live-ish TBA data:
- `tba_service.get_event_rankings(event_key)` — current rankings
- `tba_service.get_team_events(team_key, year)` + `get_team_event_status()` — past performance

Consider caching TBA responses briefly (even just in-memory or session) to avoid hammering the API when viewing multiple matches.

### Analytics Service (web/services/analytics_service.py)
- `get_team_match_averages(team_id, event_id)` — avg scouting stats across all outcomes at this event
- `get_team_match_summary(team_id, event_id)` — averages + count + min/max for display

## Files to Create
- `templates/matches/prep_list.html`
- `templates/matches/prep_detail.html`
- `web/routes/matches.py` (implement prep routes)
- `web/services/analytics_service.py`
- Possibly `web/services/cache_service.py` (simple TBA response cache)

## Dependencies
Chunks 1-4, 5-6 (need scouting data to display), Chunk 3 (TBA service)

## Definition of Done
- Match prep list shows 9771's matches
- Match prep detail shows all 6 teams grouped by alliance
- TBA past performance and current rank displayed
- Scouting averages displayed
- Robot build info displayed
- Alliance color coding (red/blue sections)
- Mobile-friendly card layout
