# Chunk 5: Scout a Robot (UI Flow 3.D)

## Goal
Build the robot scouting flow — quick, 3-click input for robot build characteristics.

## Context
Scouting a robot = recording what a robot CAN do (its build). This is separate from match outcomes. For the 2025-2026 "Rebuilt" game, we track: drive system, ground intake, shooter system, climb capability.

Users should complete scouting in ~3 clicks + save.

## Tasks

### Team List Page
**Route:** `GET /scout/robot`
**Template:** `templates/scouting/robot_list.html`

- List all teams at the current event
- Each row: team number, team name
- Indicator showing if robot has already been scouted (green check vs gray dash)
- Tap a team → go to robot scouting input

### Robot Scouting Input
**Route:** `GET /scout/robot/<team_number>`
**Template:** `templates/scouting/robot_input.html`

Layout (top to bottom):
1. Team number + name at top (big, clear)
2. **Drive System** — two big buttons side by side: "Tank" / "Swerve"
3. **Ground Intake** — two buttons: "Yes" / "No"
4. **Shooter System** — two buttons: "Fixed" / "Turret"
5. **Climb** — four buttons in a row: "None" / "L1" / "L2" / "L3"
6. **Big Save Button** at bottom

Buttons use toggle behavior — tap to select, selected button is highlighted (primary color), others are outline. Only one selection per group.

### Save Flow
**Route:** `POST /scout/robot/<team_number>`

- Confirmation modal on save: "Save scouting data for Team XXXX?"
- On confirm: save to Robot table (upsert — create or update)
- JSONB scouting_data: `{"drive_system": "swerve", "ground_intake": true, "shooter_system": "fixed", "climb": "L2"}`
- After save: redirect back to team list with success flash
- If robot was previously scouted, pre-populate buttons with existing data

### Robot Service (web/services/robot_service.py)
- `get_robot(team_id, game_id)` — fetch existing scouting data
- `save_robot(team_id, game_id, scouting_data)` — upsert robot record
- `get_scouted_status(event_id, game_id)` — returns dict of team_id → bool for scouted indicator

## Files to Create
- `templates/scouting/robot_list.html`
- `templates/scouting/robot_input.html`
- `web/services/robot_service.py`
- `web/routes/scouting.py` (add robot routes)
- `static/js/scouting.js` — button toggle logic, save confirmation

## Dependencies
Chunks 1-4 (DB, UI, TBA teams imported, navigation)

## Definition of Done
- User can browse teams at event
- User can scout a robot in 3 taps + save
- Data persists in Robot table
- Previously scouted robots show existing data
- Scouted/not-scouted indicators on team list
