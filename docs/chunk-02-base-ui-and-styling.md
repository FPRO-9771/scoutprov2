# Chunk 2: Base UI & Styling

## Goal
Establish the visual foundation — base template, styling, custom font, user login flow, and event selection.

## Context
Mobile-first design. Most users are on phones/iPads at competition venues. Follow GPro's look/feel: deep purple primary (#2F055A), Bootstrap 5, SD Glitch custom font for branding. Keep it fun and easy — these are high school students doing the scouting.

## Tasks

### Base Template (templates/base.html)
- Bootstrap 5.3 from CDN + Bootstrap Icons
- Mobile viewport meta tag
- Navbar with ScoutPro brand (SD Glitch font)
- Show current user + event in navbar when set
- Flash message support
- Block structure: title, content, scripts

### Styling (static/css/styles.css)
GPro color palette:
```css
--bs-primary: #2F055A    /* Deep purple */
--bs-info: #5a7a8a       /* Teal/slate */
--bs-success: #5a8a6e    /* Forest green */
--bs-warning: #c9a87c    /* Warm amber */
--bs-danger: #a85a6e     /* Dusty rose */
```

Mobile-first additions:
- Large touch targets (min 48px)
- Big, easy-to-tap buttons
- Readable font sizes on small screens
- Minimal horizontal scrolling

### Custom Font
- Copy SD Glitch font (from GPro's static/fonts/gpro-brand.ttf) to static/fonts/
- @font-face declaration
- `.brand-logo` class for navbar

### API Utilities (static/js/api.js)
- Fetch wrapper with JSON handling
- Error/success flash helpers
- Same pattern as GPro

### User Login Flow
**Route:** `GET/POST /login`
- Page shows list of existing users (all are team 9771 in v1)
- "Select" button next to each user
- "Create New User" form at bottom (just username — auto-associated with team 9771)
- On select/create: set session + cookie (long expiry for convenience)
- Redirect to event selection

**Route:** `GET /logout`
- Clear session, redirect to login

### Event Selection
**Route:** `GET /events`
- List of events for the current game
- Show event name, location, date
- Select button → set event in session → redirect to home

### Cookie Persistence
- Store selected user ID in a long-lived cookie
- On return visit, auto-select user if cookie present
- Still allow switching users

## Files to Create/Modify
- `templates/base.html`
- `templates/login.html`
- `templates/events.html`
- `static/css/styles.css`
- `static/js/api.js`
- `static/fonts/` (copy font file)
- `web/routes/main.py` — login, logout, event selection routes
- `web/services/user_service.py`

## Dependencies
Chunk 1 (project structure, models, DB)

## Definition of Done
- App boots with styled pages
- User can select/create a user
- User can select an event
- Session persists across page loads
- Looks good on mobile (test with browser dev tools)
