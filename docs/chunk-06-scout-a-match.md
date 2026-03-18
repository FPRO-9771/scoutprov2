# Chunk 6: Scout a Match (UI Flow 3.C)

## Goal
Build the match scouting flow — record how a specific team performed in a specific match.

## Context
Match scouting = recording what happened during a match for one team. Each match has 6 robots (3 red, 3 blue). If all 6 are scouted, we get 6 Outcome rows with the same match_id.

For "Rebuilt" 2025-2026, we track two phases: Autonomous and Teleop.

## Tasks

### Match List Page
**Route:** `GET /scout/match`
**Template:** `templates/scouting/match_list.html`

- Grid of match number buttons, 5 per row
- Buttons are numbered (Q1, Q2, Q3... or just 1, 2, 3...)
- Big, easy to tap
- Color coding: matches with all 6 teams scouted = green, partial = yellow, none = gray

### Team Selection for Match
**Route:** `GET /scout/match/<match_id>`
**Template:** `templates/scouting/match_teams.html`

- Show match number at top
- List all 6 teams, grouped by Red / Blue alliance
- Each team row shows: team number, team name, scout count badge (e.g., "2x scouted")
- Tap a team → go to match scouting input

### Match Scouting Input
**Route:** `GET /scout/match/<match_id>/team/<team_number>`
**Template:** `templates/scouting/match_input.html`

**Tabs at top:** Auton | Teleop

**Auton Tab:**
- **Balls** — 6 buttons horizontally:
  - Red X (0), 1 ball, 2 balls, 3 balls, 4 balls, 5 balls
  - Use yellow circle/ball indicators for 1-5
- **Climb** — 4 buttons horizontally:
  - Red X (0), 1, 2, 3

**Teleop Tab:**
- **Balls** — same as Auton (6 buttons)
- **Defense** — 4 buttons horizontally:
  - Red X (0), one bicep emoji (1), two biceps (2), three biceps (3)
  - Use 💪 emoji
- **Climb** — same as Auton (4 buttons)

**Big Save Button** at bottom of page (visible in both tabs)

### Save Flow
**Route:** `POST /scout/match/<match_id>/team/<team_number>`

- Confirmation modal: "Save match scouting for Team XXXX in Match YY?"
- Save to Outcome table with current user_id
- JSONB: `{"auton_balls": 3, "auton_climb": 1, "teleop_balls": 4, "teleop_climb": 2, "teleop_defense": 1}`
- After save: redirect to match team list with success flash
- Note: multiple users CAN scout the same team in the same match (unique on match+team+user)

### Button UX Details
- Selected state: filled/solid button in category color
- Unselected: outline button
- Red X buttons use danger color
- Ball buttons use warning/gold color
- Climb buttons use info color
- Defense buttons use success color
- Only one selection per group (radio-style toggle)

### Outcome Service (web/services/outcome_service.py)
- `save_outcome(match_id, team_id, user_id, scouting_data)` — create outcome record
- `get_match_scout_counts(match_id)` — returns dict of team_id → count of outcomes
- `get_event_match_scout_status(event_id)` — for match list coloring (all/partial/none)
- `get_outcome(match_id, team_id, user_id)` — fetch existing (for edit)

## Files to Create
- `templates/scouting/match_list.html`
- `templates/scouting/match_teams.html`
- `templates/scouting/match_input.html`
- `web/services/outcome_service.py`
- `web/routes/scouting.py` (add match scouting routes)
- `static/js/match-scouting.js` — tab switching, button toggles, save confirmation

## Dependencies
Chunks 1-4 (DB, UI, matches imported, navigation)

## Definition of Done
- Match grid displays all matches with color-coded scouting status
- User can select a match, then a team
- Scouting input has Auton/Teleop tabs with button-based input
- Data saves to Outcome table
- Scout count badges show on team list
- Works well on phone screens
