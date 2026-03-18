# Chunk 8: Team Page & Analytics

## Goal
Build the team detail page (linked from search and match prep) and analytics views for identifying scouting gaps and digesting data.

## Context
The team page is the "home" for a team in our system — everything we know about them in one place. Analytics help the team leads see what scouting work is still needed and make sense of accumulated data.

## Tasks

### Team Page
**Route:** `GET /teams/<team_number>`
**Template:** `templates/teams/detail.html`

Layout (top to bottom):
1. **Header:** Team number + name (big)
2. **Robot Build** section (from Robot table):
   - If scouted: show drive, intake, shooter, climb as styled badges
   - If not: "Not yet scouted" with link to scout this robot
3. **Match History** section (from Outcome table):
   - Table/cards of matches this team has been scouted in
   - Each row: match number, auton balls, auton climb, teleop balls, teleop defense, teleop climb, scouted by
   - Averages row at bottom
4. **TBA Data** section:
   - Current rank at this event
   - Past event performances

### Analytics Dashboard
**Route:** `GET /analytics`
**Template:** `templates/analytics/dashboard.html`

Two main views:

#### Missing Scouting Data
- **Unscouted Robots:** list of teams at the event whose robot build has NOT been scouted
  - Count: "X of Y teams scouted"
  - List of unscouted teams with "Scout Now" link
- **Unscouted Match Outcomes:** matches where < 6 teams have been scouted
  - Show match number, count scouted (e.g., "3/6"), list of unscouted teams
  - "Scout Now" link per team

#### Team Performance Summary
- Sortable table of all teams at the event
- Columns: Team #, Name, Avg Auton Balls, Avg Auton Climb, Avg Teleop Balls, Avg Teleop Defense, Avg Teleop Climb, # Matches Scouted
- Color coding: green for high values, red for low (helps spot strong/weak teams quickly)
- Sort by any column (client-side JS sort is fine)

### Analytics Service Additions (web/services/analytics_service.py)
- `get_unscouted_robots(event_id, game_id)` — teams without Robot record
- `get_unscouted_matches(event_id)` — matches with < 6 outcomes
- `get_all_team_averages(event_id)` — summary stats for all teams at event
- `get_team_outcomes(team_id, event_id)` — all outcome records for one team

## Files to Create
- `templates/teams/detail.html`
- `templates/analytics/dashboard.html`
- `web/routes/teams.py` (implement team detail)
- `web/routes/analytics.py` (new blueprint)
- `web/services/analytics_service.py` (extend)

## Dependencies
Chunks 1-6 (all core scouting data must exist)

## Definition of Done
- Team page shows robot build + match history + TBA data
- Analytics dashboard shows scouting gaps
- Performance summary table with sortable columns
- Links from analytics to scouting input screens
- Mobile-friendly layout
