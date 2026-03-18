# Testing Walkthrough

Step-by-step guide to test all ScoutPro features locally.

## Setup

### 1. Add your TBA API key

Create a `.env` file in the project root:

```
TBA_API_KEY=your_tba_key_here
```

Get a key at https://www.thebluealliance.com/account

### 2. Start fresh

```bash
source .venv/bin/activate
pip install -r requirements.txt
rm -f instance/scoutpro.db
flask db upgrade
flask seed
```

You should see output like:
```
Created team 9771 FPRO
Created game: Reefscape
Imported event ... with XX teams
Imported event ... with XX teams
```

### 3. Import match schedules (if available)

```bash
flask import-matches 2026mitvc
flask import-matches 2026mibig
```

**Note:** If match schedules haven't been published on TBA yet, this will import 0 matches. That's OK — you can create matches manually via the admin panel (see below).

### 4. Start the server

```bash
flask run --debug --port 5001
```

Open http://localhost:5001 in your browser (use phone-sized viewport in dev tools for mobile testing).

> **macOS note:** Port 5000 is often taken by AirPlay Receiver, so we use 5001.

---

## Test: Login Flow

1. You should be redirected to the **login page**
2. Type a name (e.g., "Brian") and tap **Join**
3. You should land on the **event selection** page
4. Select an event (e.g., the Traverse City or Ferris State event)
5. You should land on the **home screen** with 4 action buttons

**Verify:**
- Your name shows in the navbar
- The event name shows in the navbar
- All 4 action buttons are visible: Match Prep, Scout a Match, Scout a Robot, Analytics

## Test: Logout & Cookie Persistence

1. Tap the logout button (box-arrow icon in navbar)
2. You should land back on the login page
3. Close the browser tab, reopen http://localhost:5001
4. You should be auto-logged-in via cookie and redirected to event selection

## Test: Team Search

1. From the home screen, type `9771` in the search box and tap Go
2. You should land on the **Team 9771** detail page
3. Go back, search for a team number that doesn't exist (e.g., `9999`)
4. You should see a flash error: "Team 9999 not found"

---

## Test: Admin Panel

**Important:** You must be logged in and have an event selected before accessing the admin panel. Complete the Login Flow above first.

1. Navigate to http://localhost:5001/admin/
2. You should see 5 sections: Games, Events, Teams, Matches, TBA Sync

**Games:**
3. Tap Games — you should see "Reefscape"
4. Edit the name, save — verify it updates
5. Create a new game — verify it appears

**Events:**
6. Tap Events — you should see your imported events
7. Create a new event manually
8. Edit an existing event

**Teams:**
9. Tap Teams — shows teams at the current event
10. Add a new team (e.g., 9999 "TestBot")
11. Verify it appears in the list
12. Remove it with the X button

**Matches (create manually if TBA hasn't published them):**
13. Tap Matches — shows all matches for the current event
14. Create a new match: enter a match number (e.g., `1`) + 3 red team numbers + 3 blue team numbers
    - Use real team numbers from the event (check the Teams page for numbers)
    - Include `9771` in one alliance so it shows up in Match Prep
15. Verify the match appears in the list
16. Create a few more matches to have data to test with
17. Edit an existing match (tap pencil icon, change a team number, save)

**TBA Sync:**
18. Tap TBA Sync
19. Tap "Sync Event Teams" — should show success flash with count
20. Tap "Sync Matches" — should show success flash with count (0 if TBA hasn't published schedules yet)

---

## Test: Scout a Robot

1. From home, tap **Scout a Robot**
2. You should see a list of all teams at the event
3. All teams should show a gray dash (unscouted)
4. Tap any team (e.g., 9771)
5. You should see the robot scouting form with 4 categories:
   - Drive System: Tank / Swerve
   - Ground Intake: Yes / No
   - Shooter System: Fixed / Turret
   - Climb: None / L1 / L2 / L3
6. Tap one option per category — the selected button turns solid purple
7. Tap **Save Scouting Data**
8. Confirm in the modal
9. You should redirect back to the team list with a success flash
10. That team should now show a green checkmark

**Verify pre-population:**
11. Tap the same team again — your previous selections should be pre-filled
12. Change a value, save — it should update (not create a duplicate)

---

## Test: Scout a Match

**Prerequisite:** You need at least one match. If TBA matches aren't available, create one via Admin > Matches first.

1. From home, tap **Scout a Match**
2. You should see a grid of match numbers (5 per row)
3. All buttons should be gray (unscouted)
4. Tap match **1**
5. You should see 6 teams grouped by Red Alliance / Blue Alliance
6. Tap any team
7. You should see the match scouting form with two tabs: **Auton** and **Teleop**

**Auton tab:**
8. Tap a ball count (red X = 0, yellow 1-5) — button highlights
9. Tap a climb level (red X = 0, blue 1-3) — button highlights

**Teleop tab:**
10. Switch to Teleop tab
11. Tap balls, defense (red X = 0, green muscle emojis 1-3), and climb

**Save:**
12. Tap **Save Match Scouting**
13. Confirm in the modal
14. You should redirect back to the team list with a success flash
15. That team should now show "1x scouted" badge

**Verify multi-user:**
16. Log out, create a second user, select the same event
17. Scout the same team in the same match — it should allow it
18. The badge should now show "2x scouted"

**Verify match list coloring:**
19. Go back to the match list
20. Match 1 should be yellow (partial) since not all 6 teams are scouted
21. Scout all 6 teams in match 1 — it should turn green

---

## Test: Match Prep

**Prerequisite:** You need matches that include team 9771. Create one via Admin > Matches if needed (put 9771 in one of the alliances).

1. From home, tap **Match Prep**
2. You should see only matches where team 9771 is playing
3. Each match shows a red or blue badge (which alliance 9771 is on)
4. Tap a match
5. You should see 6 team cards grouped by alliance

**Each card may show (depending on available data):**
- Current rank (from TBA)
- Past event performances (from TBA)
- Scouting averages (if you've scouted them)
- Robot build badges (if robot has been scouted)

6. Team 9771's card should have a yellow border and "Us" badge

**Verify TBA data:**
- If your API key is valid and the season is active, you should see ranking data
- If TBA has no ranking data yet (pre-season), cards will show "No data available yet"

---

## Test: Team Page

1. Search for a team or tap a team number anywhere in the app
2. The team detail page shows:
   - Robot build (badges or "Not yet scouted" with link)
   - Match history table (all scouted matches with per-field values)
   - Averages row at bottom of table
   - TBA data (rank + past events)

---

## Test: Analytics

1. From home, tap **Analytics**

**Scouting Gaps tab:**
2. Shows count of scouted robots (e.g., "1 / 40 scouted")
3. Lists unscouted teams with "Scout Now" links
4. Shows matches with fewer than 6 teams scouted, with links to scout missing teams

**Performance tab:**
5. Sortable table of all teams with average stats
6. Tap any column header to sort
7. High values should be green, low values red
8. Team numbers link to team detail pages

---

## Test: Error Handling

1. Visit http://localhost:5001/this-does-not-exist
2. You should see the 404 page with "Page not found" and a home link
3. Visit http://localhost:5001/teams/99999
4. You should also see a 404

---

## Test: Automated Tests

```bash
pytest -v
```

All 44 tests should pass.

---

## Test: Demo Data (optional)

To populate the system with fake scouting data for a fuller test:

```bash
flask seed-demo
```

This creates a demo user, random robot builds, and match outcomes. After running, the analytics dashboard and match prep screens will have data to display.
